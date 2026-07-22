# Skills for Hermes Agent

These skills teach Hermes how to use the POST-MAIL-AUTOMATION project.

## Installing skills on a new PC

### Option 1: Copy folders manually

```powershell
# Create category folder
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\AppData\Local\hermes\skills\email"

# Copy each skill
Copy-Item -Recurse -Force "skills\mail-inbox" "$env:USERPROFILE\AppData\Local\hermes\skills\email\mail-inbox"
Copy-Item -Recurse -Force "skills\mail-translate" "$env:USERPROFILE\AppData\Local\hermes\skills\email\mail-translate"
Copy-Item -Recurse -Force "skills\mail-export" "$env:USERPROFILE\AppData\Local\hermes\skills\email\mail-export"
Copy-Item -Recurse -Force "skills\mail-aliexpress" "$env:USERPROFILE\AppData\Local\hermes\skills\email\mail-aliexpress"
```

### Option 2: Install via Hermes CLI

From the project root:
```bash
hermes skills install skills/mail-inbox
hermes skills install skills/mail-translate
hermes skills install skills/mail-export
hermes skills install skills/mail-aliexpress
```

### After installation

Run `/reload-skills` in Hermes or restart Hermes.

## Skill list

| Skill | Command | Description |
|---|---|---|
| `mail-inbox` | `python -m app` | Show 5 recent inbox messages |
| `mail-translate` | `python -m app translate <UID>` | Translate email to Russian |
| `mail-export` | `python -m app export [options]` | Export emails to text file |
| `mail-aliexpress` | `python -m app aliexpress [options]` | Track AliExpress orders |

## Requirements

- Python 3.11+
- `pip install -r app/requirements.txt`
- `app/.env` configured with IMAP and OpenRouter keys
- `app/credentials.json` (Google OAuth2 client secret)
- OAuth2 token per account (auto-created on first `python -m app`)
