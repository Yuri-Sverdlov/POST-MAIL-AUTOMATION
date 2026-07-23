```
Прочитай CONTEXT.md, затем AGENTS.md, затем tasks/TASK.md и выполни задание *TASK-010*.
```

# TASK-011 — Подготовить коммит для GitHub

## Source
Проект готов к фиксации после TASK-009 (баги REVIEW-001) и TASK-010 (чистка HTML + даты + спам-фильтр).
На ПК1 обновлён GUIDE.md, CONTEXT.md, PROJECT_LOG.md.
TASK-009 архивирован в `tasks/done/009-bugfix-review/`.
TASK-010 проверен архитектором — обнаружен баг в date filters (см. REPORT ниже).

## Задание
1. Исправить баг `_build_date_criteria` в `app/imap_client.py:146-163` — строки `from_date`/`to_date`/`before`/`after` нужно парсить в `datetime.date` через `datetime.strptime(val, "%Y-%m-%d").date()` перед передачей в `A(date_gte=...)`. Сейчас падает: `TypeError: expected datetime.date value, "<class 'str'>" received`.
2. `git add -A` (кроме `.backup_local/`, `.env`, `token.*.pickle`, `credentials.json`)
3. `git diff --cached --stat` — показать что пойдёт в коммит
4. `git commit -m "TASK-009 + TASK-010: strip_html v2, date range filters, --skip-newsletters, --help updated, GUIDE.md for new users"`
5. `git push origin main`
6. Заполнить `tasks/REPORT.md`

## Валидация
- [ ] `python -m app export --account sverdlovy@gmail.com --from-date 2026-07-23 --to-date 2026-07-23 --limit 3` — не падает
- [ ] `python -m app export --account sverdlovy@gmail.com --before 2026-07-10 --limit 3` — работает
- [ ] `git ls-remote origin refs/heads/main` = локальный HEAD
- [ ] REPORT.md заполнен