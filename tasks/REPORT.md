# REPORT.md — TASK-011 + TASK-012 + skills activation

## Status
✅ Все три шага выполнены и зафиксированы.

---

## Шаг 1 — TASK-011: коммит и пуш на GitHub

**Было выяснено:** TASK-011 уже был выполнен до начала сессии — коммит `50f2e25` (Thu Jul 23 19:22, 18 файлов, 777 строк) и push в `origin/main` уже прошли (SHA `50f2e25…` совпадал на local и на remote).

Локально висели **только устаревшие** `tasks/REPORT.md` (старый отчёт) и `tasks/TASK.md` (старая задача) — зафиксировано, что они описывают уже выполненное. Эти файлы **обновлены** в рамках шага 2.

---

## Шаг 2 — TASK-012: Unicode zero-width очистка в `strip_html()`

### Что сделано

| Файл | Изменение |
|---|---|
| `app/imap_client.py` | + пост-очистка сырых Unicode zero-width/control chars (U+2000–U+200F, U+2028–U+202F, U+034F, U+2800, U+FEFF) через `ZERO_WIDTH_RE`; + умная дедупликация строк через `_visible()` хелпер, который сравнивает строки после удаления мусорных символов |
| `tests/test_strip_html.py` | **Новый файл.** 21 тест: 11 на новый функционал + 10 на backward-compat |
| `tasks/TASK.md` | Заменён на новую задачу TASK-012 |
| `tasks/REPORT.md` | Обновлён (этот файл) |
| `tasks/TEST-REPORT-010.md` | Закоммичен (был untracked) |

### Тесты

```
$ python tests/test_strip_html.py
... (21 теста)
=== 21 passed, 0 failed (out of 21) ===
```

**11 новых тестов** (TASK-012):
- ZWSP (U+200B), ZWNJ (U+200C), ZWJ (U+200D) удаляются
- Figure Space (U+2007), CGJ (U+034F), En Quad (U+2000), Hair Space (U+200A) удаляются
- BOM (U+FEFF) удаляется
- 200× U+2800 (Braille Pattern Blank) → пустая строка
- Реальный кейс UID 84284: 448 chars мусора → 22 chars чистого текста
- Дедупликация «невидимых» строк: `X\u2800` и `X` считаются дублями
- Пустая строка и None → `""`

**10 backward-compat тестов:**
- HTML-теги удаляются
- HTML-entities (`&lt;`, `&gt;`, `&amp;`, `&nbsp;`) декодируются
- Whitespace нормализуется (множественные пробелы → один, табы → пробелы)
- Артефакт «96» в начале удаляется
- Тройные+ пустые строки схлопываются (одна пустая — сохраняется)
- Старая дедупликация одинаковых строк работает
- HTML-entity `&zwnj;` удаляется
- Чистый текст не трогается
- Кириллица + латиница сохраняются
- Многоабзацный текст сохраняет структуру

### Коммит и пуш

```
$ git commit -m "TASK-012: strip_html post-cleanup — strip raw Unicode zero-width/control chars, dedup invisible-similar lines; 21 tests"
[main 6d698f9] ... 5 files changed, 513 insertions(+), 23 deletions(-)

$ git push origin main
   50f2e25..6d698f9  main -> main

$ git ls-remote origin refs/heads/main
6d698f9655e6a43631c015fb54a202bb0ffa8335

$ git rev-parse HEAD
6d698f9655e6a43631c015fb54a202bb0ffa8335   ← совпадает с remote
```

✅ **Push прошёл, ветки синхронизированы.**

---

## Шаг 3 — Копирование 4 навыков в `~/.hermes/skills/`

### Что сделано

Скопировано 4 навыка из `G:\_My_Programming\POST-MAIL-AUTOMATION\skills\` в `C:\Users\Yuri\AppData\Local\hermes\skills\email\`:

| Навык | Откуда | Куда | Статус |
|---|---|---|---|
| `mail-inbox` | `POST-MAIL-AUTOMATION/skills/mail-inbox/` | `~/.hermes/skills/email/mail-inbox/` | ✅ загружается |
| `mail-translate` | `.../mail-translate/` | `~/.hermes/skills/email/mail-translate/` | ✅ загружается |
| `mail-export` | `.../mail-export/` | `~/.hermes/skills/email/mail-export/` | ✅ загружается |
| `mail-aliexpress` | `.../mail-aliexpress/` | `~/.hermes/skills/email/mail-aliexpress/` | ✅ загружается |

### Проверка через Hermes API

```bash
$ hermes skills list | grep -i "mail\|email"
│ himalaya             │ email                │ builtin │ builtin   │ enabled │
│ mail-aliexpress      │ email                │ local   │ local     │ enabled │
│ mail-export          │ email                │ local   │ local     │ enabled │
│ mail-inbox           │ email                │ local   │ local     │ enabled │
│ mail-translate       │ email                │ local   │ local     │ enabled │
│ email-processing     │ software-development │ local   │ local     │ enabled │
```

Все 4 навыка в категории `email` + уже существующий `email-processing` (в `software-development/`, общий гайдлайн по strip_html багам).

### Проверка через `skill_view`

| Навык | Загружается | Skill dir правильный | Frontmatter OK |
|---|---|---|---|
| `mail-inbox` | ✅ | ✅ `email\mail-inbox` | ✅ |
| `mail-export` | ✅ | ✅ `email\mail-export` | ✅ |
| `mail-translate` | ✅ | ✅ `email\mail-translate` | ✅ |
| `mail-aliexpress` | ✅ | ✅ `email\mail-aliexpress` | ✅ |

### Замечание про `hermes skills inspect`

`hermes skills inspect <name>` НЕ находит локальные навыки и предлагает hub-альтернативы (типа `agent-email-inbox` из skills.sh). Это **нормальное поведение** — `inspect` смотрит в удалённый хаб, а локальные навыки загружаются через `skill_view()` или `hermes --cli -z "..." --skills "name"`.

---

## Итог по 5 галочкам переноса в облако

| # | Галочка | Статус |
|---|---|---|
| 1 | POST-MAIL-AUTOMATION закоммичен + Unicode-fix | ✅ **ЗАКРЫТА** (коммиты `50f2e25` + `6d698f9`) |
| 2 | Hermes-навыки `mail-*` активированы | ✅ **ЗАКРЫТА** (4 навыка скопированы, загружаются) |
| 3 | Навык `home-accounting` T1–T8 зелёные | ⏳ Не начато (это проект HERMES-ALL-IN-ONE) |
| 4 | Telegram-бот + whitelist | ⏳ Не начато |
| 5 | Cron + бэкап finance.db | ⏳ Не начато |

**2 из 5 галочек закрыты.** Осталось 3 — все в проекте HERMES-ALL-IN-ONE (Фазы 4–6).

---

## Файлы этой сессии

Изменены и закоммичены в коммите `6d698f9`:
- `app/imap_client.py` (патч)
- `tests/test_strip_html.py` (новый)
- `tasks/TASK.md` (новая задача TASK-012)
- `tasks/REPORT.md` (этот файл)
- `tasks/TEST-REPORT-010.md` (был untracked, теперь в репо)

Локально скопированы (НЕ в репо POST-MAIL-AUTOMATION — это конфиг Hermes):
- `~/.hermes/skills/email/mail-inbox/`
- `~/.hermes/skills/email/mail-translate/`
- `~/.hermes/skills/email/mail-export/`
- `~/.hermes/skills/email/mail-aliexpress/`
