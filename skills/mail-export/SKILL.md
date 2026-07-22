---
name: mail-export
description: Use when the user wants to export emails to a text file with filters by date, sender, and account. Outputs a file with UID, date, time, from, subject, attachments, and body preview.
version: 1.0.0
author: POST-MAIL-AUTOMATION project
platforms: [windows]
metadata:
  hermes:
    tags: [mail, export, report, filter]
    category: mail
---

# Mail Export

Export Gmail messages to a text file with metadata.

## When to Use

- User asks to export emails, save emails to file, or dump inbox.
- User provides filters: date range, sender, limit.

## Procedure

1. Change to the project root directory (where `app/` lives).
2. Run from the project root:

```
python -m app export [options]
```

Common examples:
- Last 7 days, max 20: `python -m app export`
- Last 30 days, max 50: `python -m app export --days 30 --limit 50`
- Filter by sender: `python -m app export --from "@aliexpress" --days 90`
- Different account: `python -m app export --account sverdlovy@gmail.com --limit 10`

## Pitfalls

- Output file is `exported_emails.txt` by default. Use `--output` to change.
- `--from` filter matches the sender address (e.g., `@domain.com`).

## Verification

- File is created in the project root.
- Each email block contains UID, Date, Time, From, Subject, Attachments, Body.
