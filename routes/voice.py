# routes/voice.py
from flask import Blueprint, request, jsonify
import base64
import time
from typing import List

from services.assemblyai_client import AssemblyAIClient
from services.google_llm import GoogleLLM
from services.murf_client import MurfClient
from services.conversation_manager import ConversationManager, Mode

bp = Blueprint("voice", __name__, url_prefix="/api")

asr_client = AssemblyAIClient()
llm = GoogleLLM()
tts_client = MurfClient()
conv_manager = ConversationManager()

VALID_MODES: tuple[Mode, ...] = ("assistant", "coach", "support", "invest")


def _split_text_for_tts(text: str, max_len: int = 2800) -> List[str]:
    """
    Split text into chunks under max_len characters, preserving whole words.
    Murf limit is 3000 chars; we keep some buffer (2800).
    """
    words = text.split()
    chunks: List[str] = []
    current_words: List[str] = []
    length = 0

    for w in words:
        extra = len(w) + (1 if current_words else 0)
        if length + extra > max_len:
            if current_words:
                chunks.append(" ".join(current_words))
            current_words = [w]
            length = len(w)
        else:
            current_words.append(w)
            length += extra

    if current_words:
        chunks.append(" ".join(current_words))

    return chunks


def _tts_chunked(text: str, voice_id: str | None = None) -> List[str]:
    """
    Split text into Murf-sized chunks and synthesize each.
    Returns a list of base64-encoded audio chunks.
    """
    parts = _split_text_for_tts(text)
    audio_b64_chunks: List[str] = []

    for part in parts:
        audio_bytes = tts_client.synthesize(part, voice_id=voice_id)
        audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
        audio_b64_chunks.append(audio_b64)

    return audio_b64_chunks


@bp.route("/conversation/turn", methods=["POST"])
def conversation_turn():
    """
    Voice turn:
      multipart/form-data:
        audio: recorded audio file (audio.webm etc.)
        session_id: (optional) keep conversation context
        mode: (optional) "assistant" | "coach" | "support" | "invest"
        voice_id: (optional) Murf voice id

    Response JSON:
      session_id, mode, user_text, assistant_text,
      audio_base64 (first chunk),
      audio_base64_chunks (list of chunks),
      audio_format, metrics
    """
    if "audio" not in request.files:
        return jsonify({"error": "audio file required (field 'audio')"}), 400

    audio_file = request.files["audio"]

    session_id = request.form.get("session_id")
    raw_mode = request.form.get("mode") or "assistant"
    mode: Mode = raw_mode if raw_mode in VALID_MODES else "assistant"
    voice_id = request.form.get("voice_id") or None

    if not session_id:
        session_id = conv_manager.create_session(mode)
    else:
        conv_manager.set_mode(session_id, mode)

    try:
        t0 = time.time()
        user_text = asr_client.transcribe_file(audio_file)
        t1 = time.time()

        history = conv_manager.get_history(session_id)
        assistant_text = llm.generate_reply(user_text, history, mode=mode)
        t2 = time.time()

        audio_b64_chunks = _tts_chunked(assistant_text, voice_id=voice_id)
        t3 = time.time()

        conv_manager.add_turn(session_id, user_text, assistant_text)

        metrics = {
            "asr_ms": int((t1 - t0) * 1000),
            "llm_ms": int((t2 - t1) * 1000),
            "tts_ms": int((t3 - t2) * 1000),
            "total_ms": int((t3 - t0) * 1000),
        }

        return jsonify(
            {
                "session_id": session_id,
                "mode": mode,
                "user_text": user_text,
                "assistant_text": assistant_text,
                "audio_base64": audio_b64_chunks[0] if audio_b64_chunks else "",
                "audio_base64_chunks": audio_b64_chunks,
                "audio_format": "mp3",
                "metrics": metrics,
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/conversation/text-turn", methods=["POST"])
def conversation_text_turn():
    """
    Text-only turn (no ASR):
      JSON body:
        text: user input
        session_id: (optional)
        mode: (optional) "assistant" | "coach" | "support" | "invest"
        voice_id: (optional) Murf voice id
    """
    data = request.get_json(silent=True) or {}
    user_text = (data.get("text") or "").strip()
    if not user_text:
        return jsonify({"error": "text is required in JSON body"}), 400

    session_id = data.get("session_id")
    raw_mode = data.get("mode") or "assistant"
    mode: Mode = raw_mode if raw_mode in VALID_MODES else "assistant"
    voice_id = data.get("voice_id") or None

    if not session_id:
        session_id = conv_manager.create_session(mode)
    else:
        conv_manager.set_mode(session_id, mode)

    try:
        t0 = time.time()
        history = conv_manager.get_history(session_id)
        assistant_text = llm.generate_reply(user_text, history, mode=mode)
        t1 = time.time()

        audio_b64_chunks = _tts_chunked(assistant_text, voice_id=voice_id)
        t2 = time.time()

        conv_manager.add_turn(session_id, user_text, assistant_text)

        metrics = {
            "asr_ms": 0,
            "llm_ms": int((t1 - t0) * 1000),
            "tts_ms": int((t2 - t1) * 1000),
            "total_ms": int((t2 - t0) * 1000),
        }

        return jsonify(
            {
                "session_id": session_id,
                "mode": mode,
                "user_text": user_text,
                "assistant_text": assistant_text,
                "audio_base64": audio_b64_chunks[0] if audio_b64_chunks else "",
                "audio_base64_chunks": audio_b64_chunks,
                "audio_format": "mp3",
                "metrics": metrics,
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500
