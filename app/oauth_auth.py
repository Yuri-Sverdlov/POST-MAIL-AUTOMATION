from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle

SCOPES = ["https://mail.google.com/"]
CREDENTIALS_FILE = Path(__file__).parent / "credentials.json"
TOKEN_DIR = Path(__file__).parent


def _token_path(email: str) -> Path:
    safe = email.replace("@", "_at_").replace(".", "_")
    return TOKEN_DIR / f"token.{safe}.pickle"


def get_access_token(email: str) -> str:
    token_file = _token_path(email)
    creds = None
    if token_file.exists():
        with open(token_file, "rb") as f:
            creds = pickle.load(f)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_FILE), SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_file, "wb") as f:
            pickle.dump(creds, f)
    return creds.token