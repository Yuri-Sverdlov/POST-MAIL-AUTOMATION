# CONTEXT.md

## Project context
- Project name: POST-MAIL-AUTOMATION
- Purpose: AI-powered Gmail automation with LLM classification, summarization, translation.

## Stack
- Python 3.11
- `imap_tools` — IMAP client for Gmail (OAuth2/XOAUTH2)
- `google-genai` — Gemini API for translation, summaries, classification

## Roles
- Architect: defines scope, writes tasks, reviews reports.
- Terminal agent (coder @ Hermes): implements, tests, reports.

## Current focus
- Task 004: email translation to Russian via Gemini API.

## Key decisions
- Gmail access: IMAP + OAuth2 (not App Password, not Gmail REST API).
- LLM: Google Gemini (same account, free tier).
- Entry point: `python -m app` from project root.
- Imports: `from app.module import X` (package-qualified, not bare).
