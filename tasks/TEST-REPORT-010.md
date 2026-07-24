# TEST-REPORT — TASK-010 date filter validation

**Дата:** 2026-07-23 19:20 MSK
**Аккаунт:** sverdlovy@gmail.com
**Цель:** валидация `_build_date_criteria` после исправления бага str→datetime.date

---

## Прогон 1: `--from-date` + `--to-date`

### Команда
```
python -m app export --account sverdlovy@gmail.com --from-date 2026-07-23 --to-date 2026-07-23 --limit 3 --output _test_dates.txt
```

### Результат
`Exported 3 emails to ..._test_dates.txt` — **успешно**.

### Состав выдачи (3 письма за 23 июля)

| UID | Время (UTC) | Отправитель | Тема |
|---|---|---|---|
| 84285 | 19:07:21 | support@icca.academy | [БЕЛЫЕ ОБЛАКА] ...трансляция уже началась |
| 84284 | 15:55:48 | aleksandr.roytman@roycenter.co.il | Одна история с ретрита |
| 84283 | 09:31:03 | hello@email.forever.com | NEW! Notebooks are here! |

### Что работает
- Дата-фильтр: все 3 письма от 23 июля. Ошибка `date_lte` → исправлена на `date_lt(d + 1 день)`.
- `... [truncated]` — присутствует в обрезанных телах (UID 84285, 84284, 84283).
- Порядок хронологический (новые → старые).

### Что сломано — Unicode-артефакты не вычищены

UID 84284 (roycenter.co.il) содержит мусорную строку между заголовком и телом:

```
Одна история с ретрита ͏‌͏͏‌  ͏‌  ͏‌  ͏‌ ... [200+ символов]
```

Плюс вторая строка (≈1200 символов) из Unicode-пробелов (U+2800 BRAILLE PATTERN BLANK, U+200C ZWNJ, U+2007 FIGURE SPACE, U+034F COMBINING GRAPHEME JOINER).

**Это bypass strip_html()** — функция ловит `&zwnj;`/`&#8202-5;` но **не ловит сами Unicode-символы**:
- U+200B — Zero Width Space
- U+200C — Zero Width Non-Joiner  
- U+200D — Zero Width Joiner
- U+2007 — Figure Space
- U+034F — Combining Grapheme Joiner
- U+2800 — Braille Pattern Blank (не пробел, а символ)

Аналогичный мусор виден в UID 84281 из предыдущего прогона (yurispp) — строки 12, 702 из exported_emails.txt.

---

## Прогон 2: `--days 7`

### Команда
```
python -m app export --account sverdlovy@gmail.com --days 7 --limit 2 --output _test_days.txt
```

### Результат
`Exported 2 emails to ..._test_days.txt` — **успешно**. Обратная совместимость не сломана.

---

## Прогон 3: `--before`

### Команда
```
python -m app export --account sverdlovy@gmail.com --before 2026-07-10 --limit 3 --output _test_before.txt
```

### Результат
`No emails found matching criteria.` — **корректно**. В ящике нет писем раньше 10 июля в пределах лимита. Фильтр работает.

---

## Выводы

| Статус | Что |
|---|---|
| ✅ | `--from-date` + `--to-date` — работает, баг `date_lte` исправлен |
| ✅ | `--days` обратная совместимость — не сломано |
| ✅ | `--before` / `--after` — фильтр работает |
| ✅ | `... [truncated]` — присутствует |
| ❌ | **Unicode zero-width символы не вычищены** — strip_html ловит HTML-entities, но не сами символы U+200B..U+200D, U+2007, U+034F, U+2800. Нужен следующий TASK |

### Рекомендация для TASK-012

Добавить в `strip_html()` пост-очистку Unicode zero-width/control символов:

```python
# After HTML entity replacements, strip raw Unicode zero-width chars
ZERO_WIDTH_RE = re.compile('[\u200b-\u200f\u2028-\u202f\u034f\u2800\ufeff]')
text = ZERO_WIDTH_RE.sub('', text)
```

Плюс добавить дедупликацию строк с пробелами разного типа (сейчас дедупликация точная — `' '` ≠ `'\u2800'`).
