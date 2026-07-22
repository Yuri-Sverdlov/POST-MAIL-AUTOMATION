import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

IMAP_HOST = os.environ["IMAP_HOST"]
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
LLM_MODEL = os.environ.get("LLM_MODEL", "google/gemini-3.5-flash")


def get_imap_user():
    """Lazy: reads from env so --account override works."""
    return os.environ.get("IMAP_USER", "")