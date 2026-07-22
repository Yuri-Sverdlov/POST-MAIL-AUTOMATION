# REVIEW: Тест работы Hermes с Gmail (yurispp@gmail.com)

**Дата:** 2026-07-22
**Файл с результатом:** `G:\AI\_MY_PROGRAMMING\POST-MAIL-AUTOMATION\last5_yurispp.txt`

---

## Задание пользователя (полный текст)

> Хочу проверить, как ты сейчас можешь работать с почтой. Дай мне содержание пяти последних писем в `yurispp@gmail.com`. Они должны быть расположены в текстовом файле в хронологическом порядке, где явно выделены основные мета-данные.

---

## Сильные стороны

| # | Что сработало хорошо |
|---|---|
| 1 | **OAuth2** — подключение к Gmail без пароля, через XOAUTH2, с первого раза |
| 2 | **Мульти-аккаунт** — `--account yurispp@gmail.com` отработал мгновенно, токен подхватился из `token.yurispp_at_gmail_com.pickle` |
| 3 | **Экспорт** — 5 писем за 1 день корректно отобраны, сохранены в читаемый txt |
| 4 | **Мета-данные** — UID, дата, время (UTC), отправитель, тема, вложения — всё на месте, хронологический порядок соблюдён |
| 5 | **Структура файла** — разделители `====`, формат единообразный, легко парсить |

---

## Что нужно исправить (замечания пользователя + Hermes)

### Замечания пользователя

| # | Проблема | Где в файле | Где в коде |
|---|---|---|---|
| **1** | **300 символов body — слишком мало.** Письма обрываются на полуслове. | Строки 18, 74 | `imap_client.py:60` → `body = (...)[:300]` |
| **2** | **Нужен перевод иврит→русский.** Письмо от bug.co.il (стр. 44-49) на иврите — нечитаемо без перевода. | Строки 44-49 | `translator.py` — нет спецобработки иврита/RTL |

### Замечания Hermes (обнаружены при тестировании)

| # | Проблема | В файле (строка) | Причина |
|---|---|---|---|
| **3** | **Кракозябры `????????` вместо иврита** — тело письма bug.co.il не декодировано | Строка 49 | `msg.text` вернул мусор. Кодировка письма вероятно `windows-1255` или `ISO-8859-8`, а не UTF-8 |
| **4** | **HTML-письма не парсятся** — Temu: «please open this email in a high version mail client» вместо текста | Строка 34 | `imap_client.py:60` → `msg.html` отдаётся как сырой HTML, теги не удаляются |
| **5** | **Экспорт не применяет перевод** — все тела на языке оригинала | Весь файл | `export_emails()` в `imap_client.py` не вызывает `translator.py` |
| **6** | **Лимит перевода 5000 символов** — длинные письма обрезаются без предупреждения | — | `translator.py:41` → `body[:5000]` |

---

## Что конкретно править в коде

### `app/imap_client.py`

```
Строка 60:
  БЫЛО:  body = (msg.text or msg.html or "")[:300]
  НАДО:  body = strip_html(msg.text or msg.html or "")[:2000]

Строка 33 (fetch_message):
  БЫЛО:  "body": msg.text or msg.html or ""
  НАДО:  "body": strip_html(msg.text or msg.html or "")
```

Нужна функция `strip_html()`:

```python
import re

def strip_html(text: str) -> str:
    """Удалить HTML-теги, оставить читаемый текст."""
    if not text:
        return ""
    # Если выглядит как HTML — чистим
    if re.search(r'</?(html|body|div|table|a |img)', text, re.IGNORECASE):
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<[^>]+>', '\n', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r'[ \t]+', ' ', text)
        text = text.replace('&nbsp;', ' ').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
        text = '\n'.join(line.strip() for line in text.split('\n') if line.strip())
    return text
```

### `app/translator.py`

```
Строка 5 — промпт:
  БЫЛО:  "Translate the following email to Russian. Preserve formatting..."
  НАДО:  "Translate the following email to Russian. If the source is Hebrew, 
          preserve RTL direction in the translation. Preserve formatting. 
          Keep names and technical terms in original. 
          Output ONLY the translation, no explanations:\n\n"

Строка 41 — лимит:
  БЫЛО:  return _call_llm(body[:5000])
  НАДО:  MAX_BODY = 8000
          if len(body) > MAX_BODY:
              print(f"Warning: body truncated from {len(body)} to {MAX_BODY} chars")
          return _call_llm(body[:MAX_BODY])
```

### `app/imap_client.py` — `export_emails()`

Добавить флаг `--translate` для автоперевода при экспорте:

```python
def export_emails(..., translate=False):
    ...
    if translate:
        from app.translator import translate_subject, translate_body
        f.write(f"Subject (EN):  {msg.subject}\n")
        f.write(f"Subject (RU):  {translate_subject(msg.subject)}\n")
        ...
```

### `app/__main__.py`

Добавить `--translate` в парсинг аргументов `export` и `--body-limit N` для настройки размера.

### Иврит: проблема кодировки

Проверить, как `imap_tools` обрабатывает `windows-1255`. Возможно, проблема на стороне библиотеки — тогда добавить fallback:

```python
# В imap_client.py, при извлечении body:
body = msg.text or msg.html or ""
if body and '?' * 20 in body:  # признак кракозябр
    # Попробовать перечитать с явной кодировкой через raw imaplib
    ...
```

---

## Дополнительно: что стоит улучшить в проекте (системно)

| # | Что | Приоритет |
|---|---|---|
| 1 | Заменить ручной `sys.argv` на `argparse` в `__main__.py` | Средний |
| 2 | Убрать дублирование `_connect()` — сделать единую в `imap_client.py` | Высокий |
| 3 | Добавить `--help` ко всем командам | Высокий |
| 4 | Добавить retry при ошибках IMAP/API (3 попытки с backoff) | Средний |
| 5 | Исправить жёсткий путь в скиллах `.kilo/skills/` (уже исправлено при копировании в Hermes) | Готово |
| 6 | Добавить хотя бы smoke-тест: `python -m app` → проверка подключения | Средний |
| 7 | Заменить `python` на `/c/Python311/python` в документации (или добавить venv) | Низкий |

---

## Файлы для передачи агентам

```
Тестируемый файл:  G:\AI\_MY_PROGRAMMING\POST-MAIL-AUTOMATION\last5_yurispp.txt
Проект:            G:\AI\_MY_PROGRAMMING\POST-MAIL-AUTOMATION\
Этот обзор:        G:\AI\_MY_PROGRAMMING\POST-MAIL-AUTOMATION\tasks\REVIEW-001.md
```

**Инструкция архитектору:** прочитай `CONTEXT.md`, `AGENTS.md`, этот файл (`REVIEW-001.md`), изучи `last5_yurispp.txt` → напиши `tasks/TASK.md` с конкретными шагами для кодера.