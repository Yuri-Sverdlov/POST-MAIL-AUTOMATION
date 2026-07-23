# CONTEXT.md

## Project context
- Project name: POST-MAIL-AUTOMATION
- Purpose: AI-powered Gmail automation with LLM classification, summarization, translation.

## Stack
- Python 3.11
- `imap_tools` — IMAP client for Gmail (OAuth2/XOAUTH2)
- `openai` / `requests` — OpenRouter API for translation, summaries, classification
- LLM: via OpenRouter (Gemini model), not direct Gemini API

## Roles
- Architect: defines scope, writes tasks, reviews reports.
- Terminal agent (coder @ Hermes): implements, tests, reports.

## Current focus
- Task 009: fix 6 bugs + 2 system improvements from Hermes review (REVIEW-001).

## Key decisions
- Gmail access: IMAP + OAuth2 (not App Password, not Gmail REST API).
- LLM: OpenRouter API (Gemini model). API key in `app/.env` (not committed).
- Entry point: `python -m app` from project root.
- Imports: `from app.module import X` (package-qualified, not bare).
- Computer 1 path: `G:\_My_Programming\POST-MAIL-AUTOMATION`
- Computer 2 path: `G:\AI\_MY_PROGRAMMING\POST-MAIL-AUTOMATION`
