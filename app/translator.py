import json
import urllib.request
from app.config import OPENROUTER_API_KEY, LLM_MODEL

TRANSLATION_PROMPT = (
    "Translate the following email to Russian. "
    "Preserve formatting. Keep names and technical terms in original. "
    "Output ONLY the translation, no explanations:\n\n"
)


def _call_llm(text: str) -> str:
    if not text:
        return ""
    payload = {
        "model": LLM_MODEL,
        "messages": [
            {"role": "user", "content": TRANSLATION_PROMPT + text}
        ],
        "max_tokens": 4096
    }
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "HTTP-Referer": "https://github.com/Yuri-Sverdlov/POST-MAIL-AUTOMATION",
        },
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        result = json.loads(resp.read().decode())
    return result["choices"][0]["message"]["content"].strip()


def translate_subject(subject: str) -> str:
    return _call_llm(subject)


def translate_body(body: str) -> str:
    return _call_llm(body[:5000])