# config.py
import os
from dotenv import load_dotenv

load_dotenv()

ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MURF_API_KEY = os.getenv("MURF_API_KEY")

MURF_VOICE_ID = os.getenv("MURF_VOICE_ID", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

for name, value in [
    ("ASSEMBLYAI_API_KEY", ASSEMBLYAI_API_KEY),
    ("GEMINI_API_KEY", GEMINI_API_KEY),
    ("MURF_API_KEY", MURF_API_KEY),
]:
    if not value:
        raise RuntimeError(f"{name} not set in environment")
