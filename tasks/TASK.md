# TASK.md — 003: Git init, sanitize secrets, commit, push to GitHub

## Active task
Initialize git, clean up sensitive data, make the first commit, and push to GitHub.

## Context
The project is ready for version control. Remote repo already exists: https://github.com/Yuri-Sverdlov/POST-MAIL-AUTOMATION. This task must ensure ZERO secrets leak into the public repo.

## Steps

### 1. Sanitize secrets BEFORE git init
- Open `app/.env` and remove the `IMAP_PASSWORD=tpvc qfml ervf gegm` line. OAuth2 is now primary — this App Password line is dead code and a security risk.
- Leave only:
  ```
  IMAP_HOST=imap.gmail.com
  IMAP_USER=yurispp@gmail.com
  ```
- Verify: `git check-ignore -v app/.env` should show the ignore rule BEFORE any git add.

### 2. Git init and first commit
```powershell
git init
git add .
git status  # verify app/.env, credentials.json, token.pickle are NOT staged
git commit -m "Initial commit: IMAP client with OAuth2 for Gmail"
```

### 3. Set remote and push
```powershell
git remote add origin https://github.com/Yuri-Sverdlov/POST-MAIL-AUTOMATION.git
git branch -M main
git push -u origin main
```

### 4. Verify push
```powershell
git ls-remote origin refs/heads/main
git rev-parse HEAD
```
Both should return the same commit hash.

### 5. Verify no secrets leaked
- Open https://github.com/Yuri-Sverdlov/POST-MAIL-AUTOMATION in browser.
- Confirm `app/.env`, `app/credentials.json`, `app/token.pickle` are NOT in the file list.

## Validation checklist
- [ ] `app/.env` no longer contains `IMAP_PASSWORD`
- [ ] `git status` does NOT show `app/.env`, `credentials.json`, `token.pickle` as staged
- [ ] `git push` succeeds (HTTPS, Windows Credential Manager or PAT)
- [ ] `git ls-remote` commit matches local HEAD
- [ ] GitHub repo shows all source files but NO secrets

## Security notes
- The App Password was `tpvc qfml ervf gegm`. Even though `.gitignore` blocks `.env`, remove the line to be safe. Revoke this App Password at https://myaccount.google.com/apppasswords after push.
- `token.pickle` is excluded by `.gitignore` — verified locally.
