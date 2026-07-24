import re
from datetime import datetime, timedelta, timezone
import os
from imap_tools import MailBox, A, AND
from app.config import IMAP_HOST, get_imap_user
from app.oauth_auth import get_access_token


def strip_html(text: str) -> str:
    if not text:
        return ""

    # Normalise line endings first
    text = text.replace('\r\n', '\n')

    # Strip HTML tags only if content looks like HTML
    if re.search(r'</?(html|body|div|table|a |img)', text, re.IGNORECASE):
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<[^>]+>', '\n', text)

    # Normalise whitespace
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)

    # HTML entities — standard + zero-width
    text = text.replace('&nbsp;', ' ')
    text = text.replace('&amp;', '&')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('&zwnj;', '')
    text = text.replace('&zwsp;', '')
    text = re.sub(r'&#820[2-5];', '', text)

    # Strip raw Unicode zero-width / control chars (post-entity cleanup).
    # Covers: U+2000..U+200A (En Quad, Figure Space, Hair Space, ...),
    #         U+200B..U+200F (ZWSP, ZWNJ, ZWJ, LRM, RLM),
    #         U+2028..U+202F (line/paragraph/word-joiner separators),
    #         U+034F (Combining Grapheme Joiner),
    #         U+2800 (Braille Pattern Blank — looks like space, is a char),
    #         U+FEFF (BOM).
    ZERO_WIDTH_RE = re.compile(r'[\u2000-\u200f\u2028-\u202f\u034f\u2800\ufeff]')
    text = ZERO_WIDTH_RE.sub('', text)

    # Strip each line; preserve single blank line between paragraphs
    raw_lines = text.split('\n')
    lines = []
    blank_streak = 0
    for line in raw_lines:
        stripped = line.strip()
        if stripped:
            lines.append(stripped)
            blank_streak = 0
        else:
            blank_streak += 1
            if blank_streak == 1 and lines:
                lines.append('')
    if not lines:
        return ""

    # Remove isolated number artifact (1-999) on first line
    if re.match(r'^\d{1,3}$', lines[0]):
        lines = lines[1:]

    # Deduplicate consecutive identical lines — keep one.
    # Compare on "visible" content (after stripping zero-width chars), so that
    # lines like "X" and "X\u2800" are treated as duplicates.
    def _visible(s: str) -> str:
        return ZERO_WIDTH_RE.sub('', s)

    deduped = []
    for line in lines:
        if line == '':
            deduped.append(line)
        elif deduped and _visible(deduped[-1]) != '' and _visible(deduped[-1]) == _visible(line):
            continue
        else:
            deduped.append(line)

    # Normalise: no leading/trailing blank lines
    while deduped and deduped[0] == '':
        deduped = deduped[1:]
    while deduped and deduped[-1] == '':
        deduped = deduped[:-1]

    return '\n'.join(deduped)


def _decode_body(msg) -> str:
    body = msg.text or msg.html or ""
    if body and '?' * 10 in body:
        try:
            payload = msg.obj.get_payload(decode=True)
            if payload:
                for enc in ['windows-1255', 'iso-8859-8', 'cp1255']:
                    try:
                        decoded = payload.decode(enc)
                        if '?' * 10 not in decoded:
                            body = decoded
                            break
                    except Exception:
                        continue
        except Exception:
            pass
    return strip_html(body)


def _truncate_with_indicator(body: str, max_chars: int = 2000) -> str:
    if len(body) <= max_chars:
        return body
    return body[:max_chars].rstrip() + "\n... [truncated]"


NEWSLETTER_DOMAINS = (".aliexpress.com", ".puzat.ru")
NEWSLETTER_KEYWORDS = ("unsubscribe", "отписаться", "отписать")


def _is_newsletter(msg) -> bool:
    from_lower = msg.from_.lower()
    # Extract domain from email address for matching
    domain_part = from_lower.split('@')[-1] if '@' in from_lower else from_lower
    for domain in NEWSLETTER_DOMAINS:
        if domain in from_lower or domain.lstrip('.') in domain_part:
            return True
    body = (msg.text or msg.html or "").lower()
    for kw in NEWSLETTER_KEYWORDS:
        if kw in body:
            return True
    return False


def connect():
    user = get_imap_user()
    token = get_access_token(user)
    return MailBox(IMAP_HOST).xoauth2(user, token)


def list_inbox(limit=5):
    with connect() as mailbox:
        messages = [msg for msg in mailbox.fetch(A(all=True), limit=limit, reverse=True)]
        for msg in messages:
            print(f"[{msg.uid}] {msg.date} | {msg.from_} -> {msg.subject}")
        print(f"\nTotal in INBOX: {len(messages)} messages shown (limit={limit})")


def fetch_message(uid: str):
    with connect() as mailbox:
        msgs = list(mailbox.fetch(A(uid=uid), limit=1))
        if not msgs:
            return None
        msg = msgs[0]
        return {
            "uid": msg.uid,
            "date": str(msg.date),
            "from": msg.from_,
            "subject": msg.subject,
            "body": _decode_body(msg)
        }


def _build_date_criteria(days=None, from_date=None, to_date=None, before=None, after=None):
    parts = []
    now = datetime.now(timezone.utc)
    if from_date:
        d = datetime.strptime(from_date, "%Y-%m-%d").date() if isinstance(from_date, str) else from_date
        parts.append(A(date_gte=d))
    elif days is not None:
        since = (now - timedelta(days=days)).date()
        parts.append(A(date_gte=since))
    if to_date:
        d = datetime.strptime(to_date, "%Y-%m-%d").date() if isinstance(to_date, str) else to_date
        parts.append(A(date_lt=d + timedelta(days=1)))
    if before:
        d = datetime.strptime(before, "%Y-%m-%d").date() if isinstance(before, str) else before
        parts.append(A(date_lt=d))
    if after:
        d = datetime.strptime(after, "%Y-%m-%d").date() if isinstance(after, str) else after
        parts.append(A(date_gte=d))
    if not parts:
        since = (now - timedelta(days=7)).date()
        parts.append(A(date_gte=since))
    return AND(*parts)


def export_emails(days: int = 7, limit: int = 20, output: str = "exported_emails.txt",
                  from_filter: str = None, translate: bool = False,
                  from_date: str = None, to_date: str = None,
                  before: str = None, after: str = None,
                  skip_newsletters: bool = False):
    criteria = _build_date_criteria(days=days, from_date=from_date, to_date=to_date,
                                    before=before, after=after)
    if from_filter:
        criteria = AND(criteria, A(from_=from_filter))

    with connect() as mailbox:
        messages = list(mailbox.fetch(criteria, limit=limit, reverse=True))
        if not messages:
            print("No emails found matching criteria.")
            return

        with open(output, "w", encoding="utf-8") as f:
            count = 0
            for msg in messages:
                if skip_newsletters and _is_newsletter(msg):
                    continue
                count += 1
                dt = msg.date
                has_attachments = bool(msg.attachments)
                f.write("=" * 60 + "\n")
                f.write(f"UID:        {msg.uid}\n")
                f.write(f"Date:       {dt.strftime('%Y-%m-%d')}\n")
                f.write(f"Time:       {dt.strftime('%H:%M:%S')} (UTC)\n")
                f.write(f"From:       {msg.from_}\n")
                f.write(f"Subject:    {msg.subject}\n")
                f.write(f"Attachments: {'Yes' if has_attachments else 'No'}\n")
                f.write("---\n")
                body = _decode_body(msg)
                body = _truncate_with_indicator(body, 2000)
                if translate:
                    from app.translator import translate_subject, translate_body
                    f.write(f"Subject (original):  {msg.subject}\n")
                    f.write(f"Subject (translated): {translate_subject(msg.subject)}\n")
                    f.write("---\n")
                    f.write(f"Body (translated):\n{translate_body(body)[:2000]}\n")
                else:
                    f.write(f"Body (first 2000 chars):\n{body}\n")
                f.write("=" * 60 + "\n\n")

        abs_path = os.path.abspath(output)
        print(f"Exported {count} emails to {abs_path}")