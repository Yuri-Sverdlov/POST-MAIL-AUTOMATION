﻿# REPORT.md — TASK-009

## Status
Completed. All 6 bugs fixed + 2 system improvements applied.

## Changes

### BUG 1: HTML emails show raw tags
File: app/imap_client.py
- Added strip_html() — removes style/script/tags, normalises whitespace, decodes HTML entities
- Applied in both fetch_message() and export_emails() via _decode_body()

### BUG 2: Body truncated at 300 chars
File: app/imap_client.py:export_emails()
- Changed [:300] to [:2000]

### BUG 3: Hebrew text shows as ????????
File: app/imap_client.py
- Added _decode_body() helper: detects mojibake ('?' * 10), tries raw payload decode with windows-1255 / iso-8859-8 / cp1255
- Applied in both fetch_message() and export_emails()

### BUG 4: Translation not applied in export mode
File: app/imap_client.py:export_emails() + app/__main__.py
- Added translate=False parameter to export_emails()
- When True: writes original subject + translated subject + translated body
- Added --translate flag in __main__.py export arg parser

### BUG 5: Translation prompt doesn't handle Hebrew RTL
File: app/translator.py
- Added RTL handling instruction to TRANSLATION_PROMPT

### BUG 6: Translation truncates body silently
File: app/translator.py
- Added MAX_BODY = 8000 (was hardcoded 5000)
- translate_body() now prints warning when truncating

### SYS 1: Add --help to all commands
File: app/__main__.py
- Added help/--help/-h handler showing all commands and options

### SYS 2: Fix duplicate _connect() in aliexpress.py
File: app/aliexpress.py
- Removed _connect() function (duplicate of imap_client.connect)
- Imported connect from app.imap_client
- Replaced _connect() call with connect()

## Validation
- python -m app help — works, shows all commands
- python -m app — fails at credentials.json (expected, no OAuth creds in env)
- python -m app translate 20825 — fails at credentials.json (same)
- All 4 modified files: syntax check passed (py_compile)

## Files changed
- app/imap_client.py — strip_html(), _decode_body(), [:2000], --translate
- app/translator.py — RTL prompt, MAX_BODY=8000, truncation warning
- app/__main__.py — --help, --translate flag
- app/aliexpress.py — removed duplicate _connect(), uses imap_client.connect
