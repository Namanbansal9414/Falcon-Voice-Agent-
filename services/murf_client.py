# services/murf_client.py
import base64
import requests

from config import MURF_API_KEY, MURF_VOICE_ID

# EXACT URL, number "1" not "l"
MURF_TTS_URL = "https://api.murf.ai/v1/speech/generate"


class MurfClient:
    def __init__(self):
        self.api_key = MURF_API_KEY
        self.voice_id = MURF_VOICE_ID

    def synthesize(self, text: str, voice_id: str | None = None) -> bytes:
        """
        Call Murf TTS and return raw audio bytes (MP3 by default).

        voice_id:
          - if provided, overrides default voice for this call
          - otherwise uses MURF_VOICE_ID from config.py
        """
        vid = voice_id or self.voice_id

        headers = {
            "api-key": self.api_key,
            "content-type": "application/json",
        }
        body = {
            "text": text,
            "voiceId": vid,
            "format": "MP3",
            "encodeAsBase64": True,
        }

        print("Calling Murf URL:", MURF_TTS_URL)

        resp = requests.post(MURF_TTS_URL, headers=headers, json=body)
        try:
            resp.raise_for_status()
        except Exception:
            print("Murf error status:", resp.status_code)
            print("Murf error body:", resp.text)
            raise

        data = resp.json()
        encoded_audio = data.get("encodedAudio")
        if not encoded_audio:
            raise RuntimeError("Murf response missing encodedAudio")

        return base64.b64decode(encoded_audio)
