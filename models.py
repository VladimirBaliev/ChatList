"""
Модуль для управления моделями нейросетей.
Содержит логику работы с моделями и их настройками.
"""
import os
from typing import List, Dict, Optional
from dotenv import load_dotenv
import db

# Загружаем переменные окружения из .env файла
# Если файл не существует, это не критично - переменные могут быть установлены в системе
try:
    # Получаем директорию, где находится этот файл
    current_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(current_dir, '.env')
    
    # Проверяем существование файла перед загрузкой
    if os.path.exists(env_path):
        load_dotenv(dotenv_path=env_path, override=False)
    else:
        # Пробуем загрузить из текущей рабочей директории
        load_dotenv(override=False)
except (OSError, IOError, Exception) as e:
    # Если не удалось загрузить .env файл, продолжаем работу
    # Переменные окружения могут быть установлены в системе
    import logging
    logging.getLogger(__name__).debug(f"Не удалось загрузить .env файл: {e}")


class ModelManager:
    """Класс для управления моделями нейросетей."""
    
    @staticmethod
    def get_active_models() -> List[Dict]:
        """Получает список активных моделей из БД."""
        return db.get_active_models()
    
    @staticmethod
    def get_all_models() -> List[Dict]:
        """Получает все модели из БД."""
        return db.get_all_models()
    
    @staticmethod
    def get_model(model_id: int) -> Optional[Dict]:
        """Получает модель по ID."""
        return db.get_model(model_id)
    
    @staticmethod
    def get_api_key(api_id: str) -> Optional[str]:
        """
        Получает API-ключ из переменной окружения.
        
        Args:
            api_id: Имя переменной окружения, где хранится API-ключ
            
        Returns:
            API-ключ или None, если ключ не найден
        """
        return os.getenv(api_id)
    
    @staticmethod
    def validate_model(model_data: Dict) -> tuple[bool, str]:
        """
        Валидирует настройки модели.
        
        Args:
            model_data: Словарь с данными модели (name, api_url, api_id, model_type)
            
        Returns:
            Кортеж (is_valid, error_message)
        """
        if not model_data.get('name'):
            return False, "Название модели не может быть пустым"
        
        if not model_data.get('api_url'):
            return False, "API URL не может быть пустым"
        
        if not model_data.get('api_id'):
            return False, "API ID (имя переменной окружения) не может быть пустым"
        
        # Проверяем, есть ли API-ключ в переменных окружения
        api_key = ModelManager.get_api_key(model_data['api_id'])
        if not api_key:
            return False, f"API-ключ не найден в переменной окружения: {model_data['api_id']}"
        
        # Валидация URL
        api_url = model_data['api_url']
        if not (api_url.startswith('http://') or api_url.startswith('https://')):
            return False, "API URL должен начинаться с http:// или https://"
        
        return True, ""
    
    @staticmethod
    def create_model(name: str, api_url: str, api_id: str, 
                    model_type: str = None, is_active: int = 1) -> int:
        """
        Создает новую модель с валидацией.
        
        Returns:
            ID созданной модели
            
        Raises:
            ValueError: Если валидация не прошла
        """
        model_data = {
            'name': name,
            'api_url': api_url,
            'api_id': api_id,
            'model_type': model_type
        }
        
        is_valid, error_message = ModelManager.validate_model(model_data)
        if not is_valid:
            raise ValueError(error_message)
        
        return db.create_model(name, api_url, api_id, model_type, is_active)
    
    @staticmethod
    def update_model(model_id: int, **kwargs) -> bool:
        """
        Обновляет модель с валидацией.
        
        Returns:
            True если обновление успешно
        """
        # Если обновляются поля, требующие валидации, проверяем их
        if 'name' in kwargs or 'api_url' in kwargs or 'api_id' in kwargs:
            model = db.get_model(model_id)
            if not model:
                raise ValueError("Модель не найдена")
            
            # Объединяем существующие данные с новыми
            model_data = dict(model)
            model_data.update(kwargs)
            
            is_valid, error_message = ModelManager.validate_model(model_data)
            if not is_valid:
                raise ValueError(error_message)
        
        return db.update_model(model_id, **kwargs)
    
    @staticmethod
    def delete_model(model_id: int) -> bool:
        """Удаляет модель."""
        return db.delete_model(model_id)
    
    @staticmethod
    def get_model_with_key(model_id: int) -> Optional[Dict]:
        """
        Получает модель с API-ключом (для использования в запросах).
        API-ключ добавляется в словарь как 'api_key'.
        
        Returns:
            Словарь с данными модели и API-ключом, или None если модель не найдена
        """
        model = db.get_model(model_id)
        if not model:
            return None
        
        model_dict = dict(model)
        api_key = ModelManager.get_api_key(model['api_id'])
        model_dict['api_key'] = api_key
        
        return model_dict
    
    @staticmethod
    def get_active_models_with_keys() -> List[Dict]:
        """
        Получает все активные модели с их API-ключами.
        
        Returns:
            Список словарей с данными моделей и API-ключами
        """
        models = ModelManager.get_active_models()
        result = []
        
        for model in models:
            model_dict = dict(model)
            api_key = ModelManager.get_api_key(model['api_id'])
            model_dict['api_key'] = api_key
            result.append(model_dict)
        
        return result


# Функции для определения типа API и работы с разными провайдерами

def get_model_type_from_url(api_url: str) -> str:
    """
    Определяет тип модели по URL API.
    
    Args:
        api_url: URL API
        
    Returns:
        Тип модели ('openai', 'deepseek', 'groq', 'unknown')
    """
    api_url_lower = api_url.lower()
    
    if 'openai.com' in api_url_lower:
        return 'openai'
    elif 'deepseek.com' in api_url_lower:
        return 'deepseek'
    elif 'groq.com' in api_url_lower:
        return 'groq'
    else:
        return 'unknown'


def normalize_model_type(model_type: str = None, api_url: str = None) -> str:
    """
    Нормализует тип модели.
    Если тип не указан, пытается определить по URL.
    
    Args:
        model_type: Тип модели
        api_url: URL API
        
    Returns:
        Нормализованный тип модели
    """
    if model_type:
        return model_type.lower()
    
    if api_url:
        return get_model_type_from_url(api_url)
    
    return 'unknown'

