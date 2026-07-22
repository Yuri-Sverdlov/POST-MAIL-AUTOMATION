# TASK.md — 008: Git commit and push all changes (tasks 004-007)

## Active task
Stage all source code changes, exclude test artifacts, commit, and push to GitHub.

## Context
Tasks 004-007 completed: translator, export, AliExpress tracker, multi-account OAuth2. Also: GUIDE.md, updated CONTEXT.md, PROJECT_LOG.md. Ready to push.

## Files to commit (source code + docs)
Modified (10):
- `.gitignore`
- `CONTEXT.md`
- `PROJECT_LOG.md`
- `app/.env.example`
- `app/__main__.py`
- `app/imap_client.py`
- `app/oauth_auth.py`
- `app/requirements.txt`
- `tasks/REPORT.md`
- `tasks/TASK.md`

New (4):
- `AGENTS.md`
- `CLAUDE.md`
- `GUIDE.md`
- `app/aliexpress.py`
- `app/config.py`
- `app/translator.py`

Wait — AGENTS.md and CLAUDE.md were in the initial commit. Let me recheck.

Actually AGENTS.md and CLAUDE.md were committed in 095e336 (initial commit). The new files from tasks 004-007 are:
- `GUIDE.md`
- `app/aliexpress.py`
- `app/config.py`
- `app/translator.py`

## Files to EXCLUDE (test artifacts, do NOT commit)
- `aliexpress_orders.txt` — test output
- `aliexpress_orders.xlsx` — test output
- `samples_aliexpress.txt` — test output

## Steps

### 1. Add test artifacts to .gitignore
Append to `.gitignore`:
```
samples_*.txt
aliexpress_orders.*
```

### 2. Verify no secrets in staged files
```powershell
git status
# Confirm token.*.pickle, credentials.json, .env are NOT staged
```

### 3. Stage and commit
```powershell
git add .
git status  # verify only intended files are staged
git commit -m "Tasks 004-007: translation, export, AliExpress tracker, multi-account OAuth2"
```

### 4. Push
```powershell
git push origin main
```

### 5. Verify
```powershell
git log --oneline -3
git ls-remote origin refs/heads/main
git rev-parse HEAD
```
All three should show the same commit hash.

## Validation checklist
- [ ] `samples_*.txt`, `aliexpress_orders.*` excluded from commit
- [ ] No secrets in commit (token files, credentials, .env)
- [ ] Push succeeds, remote = local HEAD
- [ ] GitHub shows all source files, no test artifacts

## Notes
- CRLF warnings in diff are harmless (Windows line endings) — ignore.
- Commit message should mention tasks 004-007 for traceability.
