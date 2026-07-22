---
name: mail-translate
description: Use when the user wants to translate an email to Russian. Translates both subject and body via OpenRouter LLM.
version: 1.0.0
author: POST-MAIL-AUTOMATION project
platforms: [windows]
metadata:
  hermes:
    tags: [mail, translation, russian, llm]
    category: mail
---

# Mail Translate

Translate a Gmail message to Russian.

## When to Use

- User asks to translate an email, or says "translate this message".
- User provides a UID from the inbox list.

## Procedure

1. Change to the project root directory (where `app/` lives).
2. Run from the project root:

```
python -m app translate <UID>
```

Example:
```
python -m app translate 20822
```

## Pitfalls

- UID must be a valid number from the inbox list. Run `python -m app` first to get UIDs.
- OpenRouter API key must be set in `app/.env`.

## Verification

- Output shows original subject and translation.
- Body is printed with original preview and full translation.
