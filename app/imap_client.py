import os
from pathlib import Path
from imap_tools import MailBox, A
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")


def connect():
    from app.oauth_auth import get_access_token
    token = get_access_token()
    return MailBox(os.environ["IMAP_HOST"]).xoauth2(
        os.environ["IMAP_USER"],
        token
    )


def list_inbox(limit=5):
    with connect() as mailbox:
        messages = [msg for msg in mailbox.fetch(A(all=True), limit=limit, reverse=True)]
        for msg in messages:
            print(f"[{msg.uid}] {msg.date} | {msg.from_} -> {msg.subject}")
        print(f"\nTotal in INBOX: {len(messages)} messages shown (limit={limit})")