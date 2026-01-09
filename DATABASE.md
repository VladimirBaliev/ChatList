# Схема базы данных ChatList

## Общая информация
База данных: SQLite  
Файл базы данных: `chatlist.db` (или другое имя, настраивается в `db.py`)

## Таблицы

### 1. Таблица `prompts` (Промты)
Хранит сохраненные промты (запросы пользователя).

| Поле | Тип | Ограничения | Описание |
|------|-----|-------------|----------|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Уникальный идентификатор промта |
| `date` | TEXT | NOT NULL | Дата и время создания промта (формат: ISO 8601, например '2024-01-15 10:30:00') |
| `prompt` | TEXT | NOT NULL | Текст промта (запроса) |
| `tags` | TEXT | NULL | Теги для категоризации промта (разделитель: запятая или другой символ) |

**Индексы:**
- Индекс на `date` для быстрой сортировки по дате
- Индекс на `tags` для быстрого поиска по тегам

**Пример записи:**
```
id: 1
date: '2024-01-15 10:30:00'
prompt: 'Объясни квантовую механику простыми словами'
tags: 'наука,физика,обучение'
```

---

### 2. Таблица `models` (Модели нейросетей)
Хранит информацию о доступных моделях нейросетей и их настройках API.

| Поле | Тип | Ограничения | Описание |
|------|-----|-------------|----------|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Уникальный идентификатор модели |
| `name` | TEXT | NOT NULL UNIQUE | Название модели (например, 'GPT-4', 'DeepSeek Chat', 'Llama 3') |
| `api_url` | TEXT | NOT NULL | URL API для отправки запросов (например, 'https://api.openai.com/v1/chat/completions') |
| `api_id` | TEXT | NOT NULL | Имя переменной окружения, где хранится API-ключ (например, 'OPENAI_API_KEY') |
| `is_active` | INTEGER | NOT NULL DEFAULT 1 | Флаг активности модели (1 - активна, 0 - неактивна) |
| `model_type` | TEXT | NULL | Тип модели для определения способа отправки запроса ('openai', 'deepseek', 'groq', и т.д.) |
| `created_at` | TEXT | NOT NULL | Дата и время добавления модели |

**Индексы:**
- Индекс на `is_active` для быстрого получения активных моделей
- Индекс на `name` для быстрого поиска по имени

**Примечание:** Сами API-ключи хранятся в файле `.env`, а не в базе данных. В таблице хранится только имя переменной окружения.

**Пример записи:**
```
id: 1
name: 'GPT-4'
api_url: 'https://api.openai.com/v1/chat/completions'
api_id: 'OPENAI_API_KEY'
is_active: 1
model_type: 'openai'
created_at: '2024-01-15 10:00:00'
```

---

### 3. Таблица `results` (Результаты)
Хранит сохраненные результаты ответов моделей на промты.

| Поле | Тип | Ограничения | Описание |
|------|-----|-------------|----------|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Уникальный идентификатор результата |
| `prompt_id` | INTEGER | NOT NULL | Ссылка на промт из таблицы `prompts` (FOREIGN KEY) |
| `model_id` | INTEGER | NOT NULL | Ссылка на модель из таблицы `models` (FOREIGN KEY) |
| `response` | TEXT | NOT NULL | Текст ответа модели |
| `saved_at` | TEXT | NOT NULL | Дата и время сохранения результата |
| `tokens_used` | INTEGER | NULL | Количество использованных токенов (если доступно) |
| `response_time` | REAL | NULL | Время ответа в секундах |

**Индексы:**
- Индекс на `prompt_id` для быстрого поиска результатов по промту
- Индекс на `model_id` для быстрого поиска результатов по модели
- Индекс на `saved_at` для сортировки по дате сохранения
- Составной индекс на `(prompt_id, model_id)` для быстрого поиска конкретной пары промт-модель

**Внешние ключи:**
- `prompt_id` REFERENCES `prompts(id)` ON DELETE CASCADE
- `model_id` REFERENCES `models(id)` ON DELETE CASCADE

**Пример записи:**
```
id: 1
prompt_id: 1
model_id: 1
response: 'Квантовая механика - это раздел физики, изучающий поведение частиц на атомном и субатомном уровне...'
saved_at: '2024-01-15 10:35:00'
tokens_used: 150
response_time: 2.5
```

---

### 4. Таблица `settings` (Настройки)
Хранит настройки приложения.

| Поле | Тип | Ограничения | Описание |
|------|-----|-------------|----------|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Уникальный идентификатор настройки |
| `key` | TEXT | NOT NULL UNIQUE | Ключ настройки (например, 'theme', 'timeout', 'default_models') |
| `value` | TEXT | NULL | Значение настройки (хранится как строка, при необходимости парсится) |
| `description` | TEXT | NULL | Описание настройки |
| `updated_at` | TEXT | NOT NULL | Дата и время последнего обновления |

**Индексы:**
- Индекс на `key` для быстрого поиска настройки

**Примеры записей:**
```
id: 1
key: 'theme'
value: 'dark'
description: 'Тема интерфейса (light/dark)'
updated_at: '2024-01-15 10:00:00'

id: 2
key: 'api_timeout'
value: '30'
description: 'Таймаут запросов к API в секундах'
updated_at: '2024-01-15 10:00:00'

id: 3
key: 'default_export_format'
value: 'markdown'
description: 'Формат экспорта по умолчанию (markdown/json)'
updated_at: '2024-01-15 10:00:00'
```

---

## Связи между таблицами

```
prompts (1) ──< (N) results
models  (1) ──< (N) results
```

- Один промт может иметь множество результатов (от разных моделей)
- Одна модель может иметь множество результатов (для разных промтов)
- Результат всегда связан с одним промтом и одной моделью

---

## SQL-скрипт создания таблиц

```sql
-- Таблица prompts
CREATE TABLE IF NOT EXISTS prompts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    prompt TEXT NOT NULL,
    tags TEXT
);

CREATE INDEX IF NOT EXISTS idx_prompts_date ON prompts(date);
CREATE INDEX IF NOT EXISTS idx_prompts_tags ON prompts(tags);

-- Таблица models
CREATE TABLE IF NOT EXISTS models (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    api_url TEXT NOT NULL,
    api_id TEXT NOT NULL,
    is_active INTEGER NOT NULL DEFAULT 1,
    model_type TEXT,
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_models_is_active ON models(is_active);
CREATE INDEX IF NOT EXISTS idx_models_name ON models(name);

-- Таблица results
CREATE TABLE IF NOT EXISTS results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prompt_id INTEGER NOT NULL,
    model_id INTEGER NOT NULL,
    response TEXT NOT NULL,
    saved_at TEXT NOT NULL,
    tokens_used INTEGER,
    response_time REAL,
    FOREIGN KEY (prompt_id) REFERENCES prompts(id) ON DELETE CASCADE,
    FOREIGN KEY (model_id) REFERENCES models(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_results_prompt_id ON results(prompt_id);
CREATE INDEX IF NOT EXISTS idx_results_model_id ON results(model_id);
CREATE INDEX IF NOT EXISTS idx_results_saved_at ON results(saved_at);
CREATE INDEX IF NOT EXISTS idx_results_prompt_model ON results(prompt_id, model_id);

-- Таблица settings
CREATE TABLE IF NOT EXISTS settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT NOT NULL UNIQUE,
    value TEXT,
    description TEXT,
    updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_settings_key ON settings(key);
```

---

## Примечания по реализации

1. **Даты и время:** Используется формат ISO 8601 (YYYY-MM-DD HH:MM:SS) для удобства сортировки и сравнения.

2. **API-ключи:** Хранятся в файле `.env`, а не в БД. В таблице `models` хранится только имя переменной окружения (`api_id`).

3. **Каскадное удаление:** При удалении промта или модели автоматически удаляются связанные результаты благодаря `ON DELETE CASCADE`.

4. **Флаги активности:** Используется INTEGER вместо BOOLEAN для совместимости с SQLite (0 = false, 1 = true).

5. **Теги:** Хранятся как строка с разделителями. Можно использовать запятую, точку с запятой или другой символ. При необходимости можно создать отдельную таблицу для тегов и связь many-to-many.

6. **Расширяемость:** Схема позволяет легко добавлять новые поля в таблицы при необходимости.

