# TASK.md — 009: Fix bugs found in Hermes review (REVIEW-001)

## Active task
Fix 6 bugs + 2 high-priority system improvements found by Hermes testing.

## Source
Review document: `tasks/REVIEW-001.md`  
Test output: `last5_yurispp.txt`

## Steps

### BUG 1: HTML emails show raw tags or filler text instead of content
**Where:** `app/imap_client.py:60`, `:33`  
**Problem:** Temu email shows "open this email in a high version mail client" instead of real content. `msg.html` is raw HTML, not parsed.

**Fix:** Add `strip_html()` function and apply to both `export_emails()` and `fetch_message()`.

In `app/imap_client.py`, add at top:
```python
import re

def strip_html(text: str) -> str:
    if not text:
        return ""
    if not re.search(r'</?(html|body|div|table|a |img)', text, re.IGNORECASE):
        return text
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<[^>]+>', '\n', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    text = text.replace('&nbsp;', ' ').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
    text = '\n'.join(line.strip() for line in text.split('\n') if line.strip())
    return text
```

Then in `fetch_message()` and `export_emails()`:
```python
body = strip_html(msg.text or msg.html or "")
```

### BUG 2: Body truncated at 300 chars — too short
**Where:** `app/imap_client.py:60`  
**Fix:** Change `[:300]` to `[:2000]` in `export_emails()`.

### BUG 3: Hebrew text shows as `????????`
**Where:** `app/imap_client.py` — `msg.text` returns mojibake for windows-1255 encoding  
**Problem:** `imap_tools` may not decode non-UTF-8 emails correctly.

**Fix:** In `export_emails()` and `fetch_message()`, add encoding fallback:
```python
body = msg.text or msg.html or ""
if body and '?' * 10 in body:
    # Try raw payload with explicit encoding
    try:
        payload = msg.obj.get_payload(decode=True)
        if payload:
            # Try common encodings
            for enc in ['windows-1255', 'iso-8859-8', 'cp1255']:
                try:
                    body = payload.decode(enc)
                    if '?' * 10 not in body:
                        break
                except:
                    continue
    except:
        pass
body = strip_html(body)
```

### BUG 4: Translation not applied in export mode
**Where:** `app/imap_client.py` — `export_emails()`  
**Fix:** Add `--translate` flag. When set, call `translator.translate_subject()` and `translator.translate_body()` for each email and write both original and translation.

In `export_emails()` signature:
```python
def export_emails(days=7, limit=20, output="exported_emails.txt", from_filter=None, translate=False):
```

In the loop:
```python
if translate:
    from app.translator import translate_subject, translate_body
    f.write(f"Subject (original):  {msg.subject}\n")
    f.write(f"Subject (translated): {translate_subject(msg.subject)}\n")
    f.write("---\n")
    f.write(f"Body (translated):\n{translate_body(body)[:2000]}\n")
else:
    f.write(f"Subject:    {msg.subject}\n")
    f.write("---\n")
    f.write(f"Body (first 2000 chars):\n{body[:2000]}\n")
```

### BUG 5: Translation prompt doesn't handle Hebrew RTL
**Where:** `app/translator.py:5`  
**Fix:** Update prompt:
```python
TRANSLATION_PROMPT = (
    "Translate the following email to Russian. "
    "If the source is Hebrew or Arabic, handle RTL direction correctly in the translation. "
    "Preserve formatting. Keep names and technical terms in original. "
    "Output ONLY the translation, no explanations:\n\n"
)
```

### BUG 6: Translation truncates body silently
**Where:** `app/translator.py:41`  
**Fix:** Add warning and increase limit:
```python
MAX_BODY = 8000

def translate_body(body: str) -> str:
    if len(body) > MAX_BODY:
        print(f"Warning: body truncated from {len(body)} to {MAX_BODY} chars")
    return _call_llm(body[:MAX_BODY])
```

### SYSTEM IMPROVEMENT 1: Add `--help` to all commands
**Where:** `app/__main__.py`  
**Fix:** Add `help` mode:
```python
if len(sys.argv) > 1 and sys.argv[1] in ("help", "--help", "-h"):
    print("POST-MAIL-AUTOMATION\n")
    print("Commands:")
    print("  python -m app                                    Show 5 recent inbox messages")
    print("  python -m app translate <UID>                    Translate email to Russian")
    print("  python -m app export [options]                   Export emails to text file")
    print("  python -m app aliexpress [options]               Track AliExpress orders")
    print("\nOptions for export:")
    print("  --days N        Last N days (default 7)")
    print("  --limit N       Max emails (default 20)")
    print("  --from ADDR     Filter by sender")
    print("  --output FILE   Output filename (default exported_emails.txt)")
    print("  --translate     Auto-translate bodies to Russian")
    print("  --account EMAIL Switch Gmail account")
    print("\nOptions for aliexpress:")
    print("  --days N        Last N days (default 365)")
    print("  --limit N       Max emails (default 200)")
    print("  --account EMAIL Switch Gmail account")
    sys.exit(0)
```

### SYSTEM IMPROVEMENT 2: Fix duplicate `_connect()` in `aliexpress.py`
**Where:** `app/aliexpress.py`  
**Problem:** `aliexpress.py` has its own `_connect()` duplicating `imap_client.connect()`.

**Fix:** Delete `_connect()` from `aliexpress.py`. Import and use `connect` from `imap_client`:
```python
from app.imap_client import connect

def fetch_aliexpress_emails(days=90, limit=100):
    since = (datetime.now(timezone.utc) - timedelta(days=days)).date()
    with connect() as mailbox:
        ...
```

## Test commands after fixes
```bash
python -m app help
python -m app export --days 1 --limit 5 --translate
python -m app translate 20825   # Hebrew email — check RTL translation
```

## Deliverables
- `app/imap_client.py` — strip_html(), body limit 2000, --translate flag, encoding fallback
- `app/translator.py` — RTL prompt, truncation warning, 8000 char limit
- `app/__main__.py` — --help mode, --translate argument
- `app/aliexpress.py` — remove duplicate _connect()

## Validation
- [ ] `python -m app help` shows all commands
- [ ] Exported emails show clean text (no HTML tags, no filler messages)
- [ ] Hebrew email body shows readable chars (not ????????)
- [ ] `--translate` produces both original and translated text
- [ ] No regressions: `python -m app`, `translate`, `aliexpress` still work
