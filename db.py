"""
Модуль для работы с базой данных SQLite.
Инкапсулирует все операции с БД.
"""
import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple


DB_NAME = "chatlist.db"


def get_db_path() -> str:
    """Возвращает путь к файлу базы данных."""
    return DB_NAME


def get_connection() -> sqlite3.Connection:
    """Создает и возвращает соединение с базой данных."""
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row  # Для доступа к полям по имени
    return conn


def init_database() -> None:
    """Инициализирует базу данных и создает все необходимые таблицы."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Таблица prompts
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS prompts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                prompt TEXT NOT NULL,
                tags TEXT
            )
        """)
        
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_prompts_date ON prompts(date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_prompts_tags ON prompts(tags)")
        
        # Таблица models
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS models (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                api_url TEXT NOT NULL,
                api_id TEXT NOT NULL,
                is_active INTEGER NOT NULL DEFAULT 1,
                model_type TEXT,
                created_at TEXT NOT NULL
            )
        """)
        
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_models_is_active ON models(is_active)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_models_name ON models(name)")
        
        # Таблица results
        cursor.execute("""
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
            )
        """)
        
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_results_prompt_id ON results(prompt_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_results_model_id ON results(model_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_results_saved_at ON results(saved_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_results_prompt_model ON results(prompt_id, model_id)")
        
        # Таблица settings
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT NOT NULL UNIQUE,
                value TEXT,
                description TEXT,
                updated_at TEXT NOT NULL
            )
        """)
        
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_settings_key ON settings(key)")
        
        conn.commit()
        
        # Добавляем начальные данные, если таблицы пусты
        _add_initial_data(cursor, conn)
        
    except sqlite3.Error as e:
        conn.rollback()
        raise Exception(f"Ошибка при инициализации БД: {e}")
    finally:
        conn.close()


def _add_initial_data(cursor: sqlite3.Cursor, conn: sqlite3.Connection) -> None:
    """Добавляет начальные данные в БД (примеры моделей и настройки)."""
    # Проверяем, есть ли уже модели
    cursor.execute("SELECT COUNT(*) as count FROM models")
    if cursor.fetchone()['count'] > 0:
        return  # Данные уже есть
    
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Добавляем примеры моделей
    initial_models = [
        ("GPT-4", "https://api.openai.com/v1/chat/completions", "OPENAI_API_KEY", 1, "openai", now),
        ("DeepSeek Chat", "https://api.deepseek.com/v1/chat/completions", "DEEPSEEK_API_KEY", 1, "deepseek", now),
        ("Groq Llama 3", "https://api.groq.com/openai/v1/chat/completions", "GROQ_API_KEY", 1, "groq", now),
    ]
    
    cursor.executemany("""
        INSERT INTO models (name, api_url, api_id, is_active, model_type, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, initial_models)
    
    # Добавляем начальные настройки
    initial_settings = [
        ("theme", "light", "Тема интерфейса (light/dark)", now),
        ("api_timeout", "30", "Таймаут запросов к API в секундах", now),
        ("default_export_format", "markdown", "Формат экспорта по умолчанию (markdown/json)", now),
    ]
    
    cursor.executemany("""
        INSERT INTO settings (key, value, description, updated_at)
        VALUES (?, ?, ?, ?)
    """, initial_settings)
    
    conn.commit()


# ==================== Функции для работы с таблицей prompts ====================

def create_prompt(prompt_text: str, tags: Optional[str] = None) -> int:
    """Создает новый промт и возвращает его ID."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO prompts (date, prompt, tags)
            VALUES (?, ?, ?)
        """, (date, prompt_text, tags))
        conn.commit()
        return cursor.lastrowid
    except sqlite3.Error as e:
        conn.rollback()
        raise Exception(f"Ошибка при создании промта: {e}")
    finally:
        conn.close()


def get_prompt(prompt_id: int) -> Optional[Dict]:
    """Получает промт по ID."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT * FROM prompts WHERE id = ?", (prompt_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_all_prompts() -> List[Dict]:
    """Получает все промты, отсортированные по дате (новые сначала)."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT * FROM prompts ORDER BY date DESC")
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def search_prompts(query: str = None, tags: str = None) -> List[Dict]:
    """Поиск промтов по тексту или тегам."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        conditions = []
        params = []
        
        if query:
            conditions.append("prompt LIKE ?")
            params.append(f"%{query}%")
        
        if tags:
            conditions.append("tags LIKE ?")
            params.append(f"%{tags}%")
        
        sql = "SELECT * FROM prompts"
        if conditions:
            sql += " WHERE " + " AND ".join(conditions)
        sql += " ORDER BY date DESC"
        
        cursor.execute(sql, params)
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def update_prompt(prompt_id: int, prompt_text: str = None, tags: str = None) -> bool:
    """Обновляет промт."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        updates = []
        params = []
        
        if prompt_text is not None:
            updates.append("prompt = ?")
            params.append(prompt_text)
        
        if tags is not None:
            updates.append("tags = ?")
            params.append(tags)
        
        if not updates:
            return False
        
        params.append(prompt_id)
        cursor.execute(f"UPDATE prompts SET {', '.join(updates)} WHERE id = ?", params)
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        conn.rollback()
        raise Exception(f"Ошибка при обновлении промта: {e}")
    finally:
        conn.close()


def delete_prompt(prompt_id: int) -> bool:
    """Удаляет промт."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM prompts WHERE id = ?", (prompt_id,))
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        conn.rollback()
        raise Exception(f"Ошибка при удалении промта: {e}")
    finally:
        conn.close()


# ==================== Функции для работы с таблицей models ====================

def create_model(name: str, api_url: str, api_id: str, model_type: str = None, is_active: int = 1) -> int:
    """Создает новую модель и возвращает ее ID."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO models (name, api_url, api_id, is_active, model_type, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, api_url, api_id, is_active, model_type, created_at))
        conn.commit()
        return cursor.lastrowid
    except sqlite3.Error as e:
        conn.rollback()
        raise Exception(f"Ошибка при создании модели: {e}")
    finally:
        conn.close()


def get_model(model_id: int) -> Optional[Dict]:
    """Получает модель по ID."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT * FROM models WHERE id = ?", (model_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_all_models() -> List[Dict]:
    """Получает все модели."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT * FROM models ORDER BY name")
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def get_active_models() -> List[Dict]:
    """Получает только активные модели."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT * FROM models WHERE is_active = 1 ORDER BY name")
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def update_model(model_id: int, name: str = None, api_url: str = None, 
                 api_id: str = None, is_active: int = None, model_type: str = None) -> bool:
    """Обновляет модель."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        updates = []
        params = []
        
        if name is not None:
            updates.append("name = ?")
            params.append(name)
        if api_url is not None:
            updates.append("api_url = ?")
            params.append(api_url)
        if api_id is not None:
            updates.append("api_id = ?")
            params.append(api_id)
        if is_active is not None:
            updates.append("is_active = ?")
            params.append(is_active)
        if model_type is not None:
            updates.append("model_type = ?")
            params.append(model_type)
        
        if not updates:
            return False
        
        params.append(model_id)
        cursor.execute(f"UPDATE models SET {', '.join(updates)} WHERE id = ?", params)
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        conn.rollback()
        raise Exception(f"Ошибка при обновлении модели: {e}")
    finally:
        conn.close()


def delete_model(model_id: int) -> bool:
    """Удаляет модель."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM models WHERE id = ?", (model_id,))
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        conn.rollback()
        raise Exception(f"Ошибка при удалении модели: {e}")
    finally:
        conn.close()


# ==================== Функции для работы с таблицей results ====================

def create_result(prompt_id: int, model_id: int, response: str, 
                  tokens_used: int = None, response_time: float = None) -> int:
    """Создает новый результат и возвращает его ID."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        saved_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO results (prompt_id, model_id, response, saved_at, tokens_used, response_time)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (prompt_id, model_id, response, saved_at, tokens_used, response_time))
        conn.commit()
        return cursor.lastrowid
    except sqlite3.Error as e:
        conn.rollback()
        raise Exception(f"Ошибка при создании результата: {e}")
    finally:
        conn.close()


def get_result(result_id: int) -> Optional[Dict]:
    """Получает результат по ID."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT * FROM results WHERE id = ?", (result_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_results_by_prompt(prompt_id: int) -> List[Dict]:
    """Получает все результаты для конкретного промта."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT r.*, m.name as model_name, p.prompt as prompt_text
            FROM results r
            JOIN models m ON r.model_id = m.id
            JOIN prompts p ON r.prompt_id = p.id
            WHERE r.prompt_id = ?
            ORDER BY r.saved_at DESC
        """, (prompt_id,))
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def get_all_results() -> List[Dict]:
    """Получает все результаты с информацией о моделях и промтах."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT r.*, m.name as model_name, p.prompt as prompt_text
            FROM results r
            JOIN models m ON r.model_id = m.id
            JOIN prompts p ON r.prompt_id = p.id
            ORDER BY r.saved_at DESC
        """)
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def delete_result(result_id: int) -> bool:
    """Удаляет результат."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM results WHERE id = ?", (result_id,))
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        conn.rollback()
        raise Exception(f"Ошибка при удалении результата: {e}")
    finally:
        conn.close()


# ==================== Функции для работы с таблицей settings ====================

def get_setting(key: str) -> Optional[str]:
    """Получает значение настройки по ключу."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
        row = cursor.fetchone()
        return row['value'] if row else None
    finally:
        conn.close()


def set_setting(key: str, value: str, description: str = None) -> None:
    """Устанавливает значение настройки."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO settings (key, value, description, updated_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(key) DO UPDATE SET
                value = excluded.value,
                description = COALESCE(excluded.description, settings.description),
                updated_at = excluded.updated_at
        """, (key, value, description, updated_at))
        conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        raise Exception(f"Ошибка при установке настройки: {e}")
    finally:
        conn.close()


def get_all_settings() -> List[Dict]:
    """Получает все настройки."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT * FROM settings ORDER BY key")
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def delete_setting(key: str) -> bool:
    """Удаляет настройку."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM settings WHERE key = ?", (key,))
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        conn.rollback()
        raise Exception(f"Ошибка при удалении настройки: {e}")
    finally:
        conn.close()

