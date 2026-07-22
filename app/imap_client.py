from datetime import datetime, timedelta, timezone
import os
from imap_tools import MailBox, A, AND
from app.config import IMAP_HOST, get_imap_user
from app.oauth_auth import get_access_token


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
            "body": msg.text or msg.html or ""
        }


def export_emails(days: int = 7, limit: int = 20, output: str = "exported_emails.txt", from_filter: str = None):
    since = (datetime.now(timezone.utc) - timedelta(days=days)).date()
    criteria = A(date_gte=since)
    if from_filter:
        criteria = AND(date_gte=since, from_=from_filter)
    with connect() as mailbox:
        messages = list(mailbox.fetch(criteria, limit=limit, reverse=True))
        if not messages:
            print(f"No emails found in the last {days} days.")
            return

        with open(output, "w", encoding="utf-8") as f:
            for msg in messages:
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
                body = (msg.text or msg.html or "")[:300]
                f.write(f"Body (first 300 chars):\n{body}\n")
                f.write("=" * 60 + "\n\n")

        abs_path = os.path.abspath(output)
        print(f"Exported {len(messages)} emails to {abs_path}")