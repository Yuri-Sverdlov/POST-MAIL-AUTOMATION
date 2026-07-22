---
name: mail-inbox
description: Use when the user asks to show recent emails, check inbox, or list Gmail messages. Shows the 5 most recent emails from the inbox.
version: 1.0.0
author: POST-MAIL-AUTOMATION project
platforms: [windows]
metadata:
  hermes:
    tags: [mail, gmail, inbox, read]
    category: mail
---

# Mail Inbox

Show recent Gmail inbox messages.

## When to Use

- User asks to see emails, check mail, or list inbox.
- User says "what's in my inbox" or "show recent messages".

## Procedure

1. Change to the project root directory (where `app/` lives).
2. Run from the project root:

```
python -m app
```

With a specific account:

```
python -m app --account other@gmail.com
```

## Pitfalls

- OAuth2 token must exist for the account. First run per account opens a browser.
- Network timeout: retry once if IMAP connection fails.

## Verification

- Output shows 5 emails with UID, date, from, subject.
- Total count is printed at the end.
