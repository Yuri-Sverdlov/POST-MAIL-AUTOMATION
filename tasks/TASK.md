```
Прочитай CONTEXT.md, затем AGENTS.md, затем tasks/TASK.md и выполни задание *TASK-012*.
```

# TASK-012 — Unicode zero-width очистка в strip_html() + дедупликация «невидимых» строк

## Source
TASK-011 (коммит `50f2e25`) закрыт. Из `tasks/TEST-REPORT-010.md` известен реальный баг: `strip_html()` ловит HTML-entities (`&zwnj;`, `&#8202-5;`), но **не ловит сырые Unicode-символы**:

- U+200B (Zero Width Space)
- U+200C (Zero Width Non-Joiner)
- U+200D (Zero Width Joiner)
- U+2007 (Figure Space)
- U+034F (Combining Grapheme Joiner)
- U+2800 (Braille Pattern Blank — **не пробел, а символ!**)
- U+FEFF (BOM)

Плюс дедупликация строк сейчас **точная** (`' '` ≠ `'\u2800'`), из-за чего строки из Unicode-пробелов считаются разными и не схлопываются.

## Цель
Пост-очистка Unicode-мусора, который приходит в теле письма и обходит текущий `strip_html()`. Чтобы тело письма от `roycenter.co.il` (UID 84284) перестало содержать 200+ символов «мусорной строки».

## План

### 1. Патч `app/imap_client.py` — функция `strip_html()`

Добавить **после** HTML-entity replacements (после строки `text = re.sub(r'&#820[2-5];', '', text)`):

```python
# Strip raw Unicode zero-width / control chars (post-entity cleanup)
ZERO_WIDTH_RE = re.compile(r'[\u200b-\u200f\u2028-\u202f\u034f\u2800\ufeff]')
text = ZERO_WIDTH_RE.sub('', text)
```

### 2. Умная дедупликация «невидимых» строк

В текущем коде (строки ~56–63):
```python
deduped = []
for line in lines:
    if line == '':
        deduped.append(line)
    elif deduped and deduped[-1] == line:
        continue
    else:
        deduped.append(line)
```

Сравнение `deduped[-1] == line` — точное. Нужно сравнивать **видимое** содержимое (после удаления всех Unicode-мусорных символов). Заменить на:

```python
def _visible(s: str) -> str:
    """Strip zero-width chars for comparison purposes only."""
    return ZERO_WIDTH_RE.sub('', s)

deduped = []
for line in lines:
    if line == '':
        deduped.append(line)
    elif deduped and _visible(deduped[-1]) == _visible(line) and _visible(line) != '':
        continue
    else:
        deduped.append(line)
```

### 3. Прогнать тест на мусорной строке из TEST-REPORT-010

Создать файл `tests/test_strip_html.py` со следующими кейсами:

```python
from app.imap_client import strip_html

# Кейс 1: ZWSP между словами
assert "  " not in strip_html("hello\u200bworld").replace("hello", "").replace("world", "")

# Кейс 2: U+2800 (Braille Pattern Blank) — длинная строка из 200+ символов
garbage = "\u2800" * 200
result = strip_html(garbage)
assert "\u2800" not in result

# Кейс 3: BOM в начале
assert strip_html("\ufeffHello") == "Hello"

# Кейс 4: ZWJ (U+200D) — дедупликация строк, которые выглядят одинаково после очистки
# до патча: две строки "X\u2800" и "X" считаются разными
# после патча: должны схлопнуться в одну
text = "X\u2800\nX\nY"
result = strip_html(text)
assert result.count("X") == 1  # осталась только одна видимая "X"

# Кейс 5: реальный кейс из TEST-REPORT-010 — UID 84284 (roycenter.co.il)
real_garbage = (
    "Одна история с ретрита \u200c\u200c\u200c \u2800 \u2800 \u2800 ... [200+ символов]\n"
    "\u200b" * 100 + "\u034f" * 50 + "\u2800" * 300
)
result = strip_html(real_garbage)
# Не должно быть 200+ символов «мусорной строки»
# Не должно быть Unicode-мусора (U+200B, U+200C, U+200D, U+2007, U+034F, U+2800, U+FEFF)
for code_point in [0x200B, 0x200C, 0x200D, 0x2007, 0x034F, 0x2800, 0xFEFF]:
    assert chr(code_point) not in result, f"U+{code_point:04X} остался в результате"
```

### 4. Обновить `GUIDE.md` — секция «Безопасность» / известные ограничения

Добавить в `GUIDE.md` короткий абзац:

```markdown
## Unicode-очистка

`strip_html()` удаляет:
- HTML-entities: `&zwnj;`, `&zwsp;`, `&#8202-5;`
- Сырые Unicode zero-width/control: U+200B–U+200F, U+2028–U+202F, U+034F, U+2800, U+FEFF
- Дедуплицирует строки, выглядящие одинаково после очистки
```

### 5. Валидация

- [ ] `python -m pytest tests/test_strip_html.py -v` — все 5 кейсов зелёные
- [ ] Реальный прогон `python -m app export --account sverdlovy@gmail.com --from-date 2026-07-23 --to-date 2026-07-23 --limit 3` — мусорная строка из UID 84284 убрана
- [ ] `git diff app/imap_client.py` — патч компактный, не сломал существующую логику
- [ ] `git diff` НЕ содержит секретов (`.env`, `token.*.pickle`, `credentials.json`)
- [ ] `git log --oneline -1` — коммит с правильным сообщением
- [ ] `git push origin main` — успешно
- [ ] `git ls-remote origin refs/heads/main` = локальный HEAD

## Файлы для изменения
- `app/imap_client.py` — патч `strip_html()` + добавить `_visible()` хелпер
- `tests/test_strip_html.py` — новый файл, 5 кейсов
- `GUIDE.md` — раздел «Unicode-очистка»
- `tasks/REPORT.md` — отчёт по факту
- `tasks/TEST-REPORT-012.md` — отчёт о прогоне теста на реальных письмах

## Подводные камни

| Символ | Что это | Почему опасен |
|---|---|---|
| U+200B (ZWSP) | Невидимый разделитель | Слово «hel\u200blo» = «hello» визуально, но другой байт |
| U+200C (ZWNJ) | Невидимый разделитель (RTL) | В иврите/арабском — критичен |
| U+200D (ZWJ) | Соединитель эмодзи | Не для текста писем |
| U+034F (CGJ) | Графемный объединитель | Невидим, не нужен |
| U+2800 (Braille Blank) | **Символ, не пробел** | LEN=1, визуально пустой |
| U+FEFF (BOM) | Маркер порядка байтов | Не должен быть в тексте |

## Сообщение коммита
```
TASK-012: strip_html post-cleanup — strip raw Unicode zero-width/control chars, dedup invisible-similar lines
```
