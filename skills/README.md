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

| Skill | Version | Command | Description |
|---|---|---|---|
| `mail-inbox` | 1.1.0 | `python -m app` | Show 5 recent inbox messages |
| `mail-translate` | 1.1.0 | `python -m app translate <UID>` | Translate email to Russian (EN/HE) |
| `mail-export` | 1.2.0 | `python -m app export [options]` | Export emails with date range, sender, translation filters |
| `mail-aliexpress` | 1.1.0 | `python -m app aliexpress [options]` | Track AliExpress orders |

### New in mail-export 1.2.0
- `--from-date` / `--to-date` — filter by date range
- `--before` / `--after` — filter relative to a date
- `--translate` — auto-translate to Russian
- `--skip-newsletters` — exclude promotional emails

## Requirements

- Python 3.11+
- `pip install -r app/requirements.txt`
- `app/.env` configured with IMAP and OpenRouter keys
- `app/credentials.json` (Google OAuth2 client secret)
- OAuth2 token per account (auto-created on first `python -m app`)
