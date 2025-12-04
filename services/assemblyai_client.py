# services/assemblyai_client.py
import io
import time
import requests
from typing import BinaryIO

from config import ASSEMBLYAI_API_KEY

ASSEMBLYAI_UPLOAD_URL = "https://api.assemblyai.com/v2/upload"
ASSEMBLYAI_TRANSCRIPT_URL = "https://api.assemblyai.com/v2/transcript"
HEADERS = {"authorization": ASSEMBLYAI_API_KEY}


class AssemblyAIClient:
    def __init__(self):
        self.headers = HEADERS

    def _upload_audio(self, file_obj: BinaryIO) -> str:
        """
        Upload raw audio bytes to AssemblyAI and return upload_url.
        """
        resp = requests.post(
            ASSEMBLYAI_UPLOAD_URL,
            headers=self.headers,
            data=file_obj.read(),
        )
        resp.raise_for_status()
        return resp.json()["upload_url"]

    def _create_transcript(self, audio_url: str) -> str:
        """
        Create a transcript job for that audio_url, return transcript_id.
        """
        resp = requests.post(
            ASSEMBLYAI_TRANSCRIPT_URL,
            headers={**self.headers, "content-type": "application/json"},
            json={"audio_url": audio_url},
        )
        resp.raise_for_status()
        return resp.json()["id"]

    def _wait_for_transcript(self, transcript_id: str, timeout_sec: int = 60) -> str:
        """
        Poll transcript until completed, return the text.
        """
        url = f"{ASSEMBLYAI_TRANSCRIPT_URL}/{transcript_id}"
        start = time.time()
        while True:
            resp = requests.get(url, headers=self.headers)
            resp.raise_for_status()
            data = resp.json()
            status = data["status"]

            if status == "completed":
                return data["text"]
            if status == "error":
                raise RuntimeError(f"AssemblyAI error: {data.get('error')}")
            if time.time() - start > timeout_sec:
                raise TimeoutError("AssemblyAI transcription timed out")

            time.sleep(1.0)

    def transcribe_file(self, file_storage) -> str:
        """
        Flask FileStorage -> transcript text.
        """
        buf = io.BytesIO(file_storage.read())
        buf.seek(0)
        audio_url = self._upload_audio(buf)
        transcript_id = self._create_transcript(audio_url)
        text = self._wait_for_transcript(transcript_id)
        return text
