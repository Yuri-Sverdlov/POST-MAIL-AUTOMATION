# GUIDE.md — Путеводитель по проекту POST-MAIL-AUTOMATION

## Что это

Инструмент для автоматизации работы с Gmail через командную строку.
Работает через IMAP + OAuth2 (не App Password, не Gmail REST API).

- **Перевод писем** на русский через ИИ.
- **Экспорт писем** в текстовый файл с фильтрами по дате и отправителю.
- **AliExpress-трекер** — отслеживание заказов с выводом в `.txt` и `.xlsx`.
- Поддержка **нескольких Gmail-аккаунтов** через `--account`.

## Быстрый старт (первый запуск)

### 1. Установка
```bash
pip install -r app/requirements.txt
```

### 2. Настройка
Скопируйте `app/.env.example` в `app/.env` и заполните:
```
IMAP_HOST=imap.gmail.com
IMAP_USER=your.email@gmail.com
OPENROUTER_API_KEY=your-openrouter-key
LLM_MODEL=google/gemini-3.5-flash
```

### 3. Авторизация Gmail
Первый запуск откроет браузер для OAuth2:
```bash
python -m app
```
Подтвердите доступ — токен сохранится в `app/token.pickle`.
Повторные запуски браузер не открывают.

### 4. Ключи API
- **Gmail OAuth2:** создайте `credentials.json` в Google Cloud Console
  (тип: Desktop application, scope: `https://mail.google.com/`).
- **Перевод (OpenRouter):** ключ на https://openrouter.ai/keys.
  Бесплатные модели: `google/gemini-3.5-flash`, `google/gemini-2.5-flash`.

---

## Команды

Все команды запускаются из корня проекта.

### `python -m app`
Показать 5 последних писем из Inbox и список доступных команд.

### `python -m app translate <UID>`
Перевести письмо на русский. UID — номер из вывода `python -m app`.
```
python -m app translate 20822
```
Переводит тему и тело письма через OpenRouter (Gemini).

### `python -m app export [опции]`
Сохранить письма в текстовый файл.

| Опция | По умолчанию | Описание |
|---|---|---|
| `--days N` | 7 | Письма за последние N дней |
| `--limit N` | 20 | Максимум N писем |
| `--output file.txt` | exported_emails.txt | Имя выходного файла |
| `--from ADDR` | нет | Фильтр по отправителю |
| `--from-date YYYY-MM-DD` | нет | Начиная с даты (включительно) |
| `--to-date YYYY-MM-DD` | нет | До даты (включительно) |
| `--before YYYY-MM-DD` | нет | Строго раньше даты |
| `--after YYYY-MM-DD` | нет | Строго позже даты |
| `--translate` | нет | Автоперевод тел писем на русский |
| `--skip-newsletters` | нет | Пропустить рассылки (спам, промо) |
| `--account EMAIL` | из .env | Переключить Gmail-аккаунт |

Примеры:
```bash
python -m app export                                              # последние 7 дней
python -m app export --days 30 --limit 50                         # месяц, до 50 писем
python -m app export --from "@aliexpress" --days 90               # только AliExpress
python -m app export --account sverdlovy@gmail.com --limit 10     # другой аккаунт
python -m app export --from-date 2026-07-01 --to-date 2026-07-31 # конкретный месяц
python -m app export --before 2026-07-10 --limit 5               # 5 писем до даты
python -m app export --days 7 --translate --skip-newsletters       # перевод без спама
```

Файл содержит для каждого письма: UID, дату, время (UTC), отправителя, тему,
наличие вложений, первые 2000 символов тела. Если тело обрезано —
добавляется `... [truncated]`.

### `python -m app aliexpress [опции]`
Отслеживание заказов AliExpress: парсит транзакционные письма,
пропускает рекламу, выдаёт два файла.

| Опция | По умолчанию | Описание |
|---|---|---|
| `--days N` | 365 | Письма за последние N дней |
| `--limit N` | 200 | Максимум N писем |
| `--account EMAIL` | из .env | Gmail-аккаунт с AliExpress |

Пример:
```bash
python -m app aliexpress --account sverdlovy@gmail.com --days 90 --limit 100
```

Выходные файлы:
- **`aliexpress_orders.txt`** — хронологический отчёт:
  дата, номер заказа, трекинг-номер, статус, тема письма.
- **`aliexpress_orders.xlsx`** — таблица Excel с колонками:
  Date | Order ID | Tracking ID | Status | Subject.

Статусы заказов (извлекаются автоматически):
- «Ожидает подтверждения» — заказ создан
- «Подтверждение продлено» — время подтверждения увеличено
- «Доставлен (ожидает отзыва)» — посылка получена
- «Доставлен до двери» — курьерская доставка

Рекламные письма AliExpress (промо, скидки, рекомендации) в отчёт **не попадают**.
Только реальные заказы и уведомления о доставке.

---

## Несколько аккаунтов

Каждый аккаунт автоматически сохраняет свой токен в `app/token.EMAIL.pickle`.
При первом переключении через `--account EMAIL` откроется браузер для входа —
один раз. Токен сохранится, и при следующих запусках браузер не потребуется.

Добавление нового аккаунта:
```bash
python -m app --account third@gmail.com
# Браузер → подтвердить доступ → готово.
```

Переключение между аккаунтами — мгновенное, без паролей:
```bash
python -m app                                    # аккаунт из .env (основной)
python -m app --account sverdlovy@gmail.com      # второй аккаунт
python -m app export --account third@example.com # третий
```

Никаких ручных копий токенов. Масштабируется на любое число аккаунтов.

---

## Структура проекта

```
POST-MAIL-AUTOMATION/
├── app/
│   ├── __init__.py              # пакет
│   ├── __main__.py              # точка входа, парсинг команд
│   ├── config.py                # загрузка .env
│   ├── oauth_auth.py            # OAuth2-авторизация Gmail
│   ├── imap_client.py           # IMAP: список, чтение, экспорт, strip_html, даты
│   ├── translator.py            # перевод через OpenRouter LLM (RTL, truncation)
│   ├── aliexpress.py            # парсер заказов AliExpress
│   ├── .env                     # ключи и настройки (НЕ коммитить!)
│   ├── .env.example             # шаблон настроек
│   ├── credentials.json         # Google OAuth2 (НЕ коммитить!)
│   └── token.pickle             # OAuth2-токен (НЕ коммитить!)
├── tasks/
│   ├── TASK.md                  # активное задание кодеру
│   ├── REPORT.md                # отчёт о выполнении
│   └── done/                    # архив принятых заданий
├── skills/                      # скиллы для Hermes-агента
├── AGENTS.md                    # правила для терминального агента
├── CONTEXT.md                   # память проекта (стек, фокус)
├── GUIDE.md                     # этот файл
└── PROJECT_LOG.md               # журнал всех сессий (append-only)
```

---

## Перенос на другой ПК

### 1. Клонирование
```bash
git clone https://github.com/Yuri-Sverdlov/POST-MAIL-AUTOMATION.git
cd POST-MAIL-AUTOMATION
```

### 2. Установка зависимостей
```bash
pip install -r app/requirements.txt
```

### 3. Настройка секретов (вручную, НЕ из git)
Создайте `app/.env` из шаблона:
```bash
copy app\.env.example app\.env
```
Заполните реальными значениями:
- `IMAP_USER` — ваш Gmail
- `OPENROUTER_API_KEY` — ключ с https://openrouter.ai/keys

Создайте `app/credentials.json`:
- Скачайте OAuth2 client secret из Google Cloud Console
  (Desktop application, scope: `https://mail.google.com/`)
- Сохраните как `app/credentials.json`

### 4. Авторизация Gmail
```bash
python -m app
# Откроется браузер → подтвердить доступ.
# Токен сохранится в app/token.ВАШ_EMAIL.pickle
```

### 5. Скиллы для терминального агента (опционально)
Скиллы лежат в папке `skills/`. Для Claude Code / Hermes:
```powershell
Copy-Item -Recurse -Force "skills\*" "$env:USERPROFILE\.agents\skills\"
```
После копирования: перезапустите агента.

### 6. Проверка
```bash
python -m app                    # показать входящие
python -m app translate 20822    # перевести письмо
python -m app export --limit 3   # экспорт 3 писем
```

---

## Стек

| Компонент | Технология |
|---|---|
| Язык | Python 3.11 |
| Почта | IMAP через `imap_tools` |
| Авторизация | Gmail OAuth2 / XOAUTH2 |
| LLM | OpenRouter API (Gemini Flash) |
| Excel | `openpyxl` |

---

## Безопасность

- **НИКОГДА не коммитить:** `app/.env`, `app/credentials.json`, `app/token.pickle`.
  Они в `.gitignore`.
- App Password **не используется** — только OAuth2.
- Ключ OpenRouter — в `app/.env`, только локально.

---

## Терминальный агент (Claude Code / Hermes)

Проект спроектирован для работы с терминальным агентом по двухагентной схеме
(архитектор в чате ↔ кодер в терминале).

Стартовая команда для кодера (копируется из начала `tasks/TASK.md`):
```
Прочитай CONTEXT.md, затем AGENTS.md, затем tasks/TASK.md и выполни задание *TASK-NNN*.
```
где `NNN` — номер активного задания.

Готовые команды для пользователя:
```
python -m app                                        # список писем
python -m app export --days 7 --limit 5              # экспорт за неделю
python -m app translate 20822                        # перевод письма
python -m app aliexpress --days 90 --limit 100       # заказы AliExpress
```
