"""
Модуль для отправки запросов к API нейросетей.
Обрабатывает различные типы API и ошибки.
"""
import requests
import time
import logging
from typing import Dict, Optional, List
from concurrent.futures import ThreadPoolExecutor, as_completed

# Настройка логирования (без вывода в консоль)
# Используем NullHandler, чтобы не выводить логи в консоль
# Логи будут записываться только через основной logger в main.py
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())
logger.setLevel(logging.WARNING)  # Только предупреждения и ошибки


class APIError(Exception):
    """Исключение для ошибок API."""
    pass


def send_request_to_openai(model_data: Dict, prompt: str, timeout: int = 30) -> Dict:
    """
    Отправляет запрос к OpenAI API.
    
    Args:
        model_data: Словарь с данными модели (должен содержать api_key, api_url)
        prompt: Текст промта
        timeout: Таймаут запроса в секундах
        
    Returns:
        Словарь с ответом: {'response': str, 'tokens_used': int, 'response_time': float}
        
    Raises:
        APIError: При ошибке запроса
    """
    api_key = model_data.get('api_key')
    api_url = model_data.get('api_url')
    
    if not api_key:
        api_id = model_data.get('api_id', 'N/A')
        raise APIError(f"API-ключ не найден. Проверьте переменную окружения '{api_id}' в файле .env")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Определяем имя модели из URL или используем по умолчанию
    model_name = model_data.get('name', 'gpt-4')
    if 'gpt-4' in model_name.lower():
        model_name = 'gpt-4'
    elif 'gpt-3.5' in model_name.lower():
        model_name = 'gpt-3.5-turbo'
    else:
        model_name = 'gpt-4'  # По умолчанию
    
    payload = {
        "model": model_name,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }
    
    start_time = time.time()
    
    try:
        response = requests.post(api_url, json=payload, headers=headers, timeout=timeout)
        response.raise_for_status()
        
        response_time = time.time() - start_time
        data = response.json()
        
        # Извлекаем ответ
        if 'choices' in data and len(data['choices']) > 0:
            response_text = data['choices'][0]['message']['content']
        else:
            raise APIError("Неожиданный формат ответа от API")
        
        # Извлекаем информацию о токенах
        tokens_used = None
        if 'usage' in data:
            tokens_used = data['usage'].get('total_tokens')
        
        logger.info(f"Запрос к {model_data.get('name')} выполнен за {response_time:.2f}с")
        
        return {
            'response': response_text,
            'tokens_used': tokens_used,
            'response_time': response_time
        }
        
    except requests.exceptions.Timeout:
        raise APIError(f"Таймаут запроса к {model_data.get('name')}")
    except requests.exceptions.RequestException as e:
        raise APIError(f"Ошибка запроса к {model_data.get('name')}: {str(e)}")


def send_request_to_deepseek(model_data: Dict, prompt: str, timeout: int = 30) -> Dict:
    """
    Отправляет запрос к DeepSeek API.
    
    Args:
        model_data: Словарь с данными модели
        prompt: Текст промта
        timeout: Таймаут запроса в секундах
        
    Returns:
        Словарь с ответом: {'response': str, 'tokens_used': int, 'response_time': float}
        
    Raises:
        APIError: При ошибке запроса
    """
    api_key = model_data.get('api_key')
    api_url = model_data.get('api_url')
    
    if not api_key:
        api_id = model_data.get('api_id', 'N/A')
        raise APIError(f"API-ключ не найден. Проверьте переменную окружения '{api_id}' в файле .env")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }
    
    start_time = time.time()
    
    try:
        response = requests.post(api_url, json=payload, headers=headers, timeout=timeout)
        response.raise_for_status()
        
        response_time = time.time() - start_time
        data = response.json()
        
        if 'choices' in data and len(data['choices']) > 0:
            response_text = data['choices'][0]['message']['content']
        else:
            raise APIError("Неожиданный формат ответа от API")
        
        tokens_used = None
        if 'usage' in data:
            tokens_used = data['usage'].get('total_tokens')
        
        logger.info(f"Запрос к {model_data.get('name')} выполнен за {response_time:.2f}с")
        
        return {
            'response': response_text,
            'tokens_used': tokens_used,
            'response_time': response_time
        }
        
    except requests.exceptions.Timeout:
        raise APIError(f"Таймаут запроса к {model_data.get('name')}")
    except requests.exceptions.RequestException as e:
        raise APIError(f"Ошибка запроса к {model_data.get('name')}: {str(e)}")


def send_request_to_groq(model_data: Dict, prompt: str, timeout: int = 30) -> Dict:
    """
    Отправляет запрос к Groq API.
    
    Args:
        model_data: Словарь с данными модели
        prompt: Текст промта
        timeout: Таймаут запроса в секундах
        
    Returns:
        Словарь с ответом: {'response': str, 'tokens_used': int, 'response_time': float}
        
    Raises:
        APIError: При ошибке запроса
    """
    api_key = model_data.get('api_key')
    api_url = model_data.get('api_url')
    
    if not api_key:
        api_id = model_data.get('api_id', 'N/A')
        raise APIError(f"API-ключ не найден. Проверьте переменную окружения '{api_id}' в файле .env")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Определяем модель из названия
    model_name = "llama-3-8b-8192"  # По умолчанию
    if 'llama-3' in model_data.get('name', '').lower():
        model_name = "llama-3-8b-8192"
    elif 'mixtral' in model_data.get('name', '').lower():
        model_name = "mixtral-8x7b-32768"
    
    payload = {
        "model": model_name,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }
    
    start_time = time.time()
    
    try:
        response = requests.post(api_url, json=payload, headers=headers, timeout=timeout)
        response.raise_for_status()
        
        response_time = time.time() - start_time
        data = response.json()
        
        if 'choices' in data and len(data['choices']) > 0:
            response_text = data['choices'][0]['message']['content']
        else:
            raise APIError("Неожиданный формат ответа от API")
        
        tokens_used = None
        if 'usage' in data:
            tokens_used = data['usage'].get('total_tokens')
        
        logger.info(f"Запрос к {model_data.get('name')} выполнен за {response_time:.2f}с")
        
        return {
            'response': response_text,
            'tokens_used': tokens_used,
            'response_time': response_time
        }
        
    except requests.exceptions.Timeout:
        raise APIError(f"Таймаут запроса к {model_data.get('name')}")
    except requests.exceptions.RequestException as e:
        raise APIError(f"Ошибка запроса к {model_data.get('name')}: {str(e)}")


def send_request_to_openrouter(model_data: Dict, prompt: str, timeout: int = 30) -> Dict:
    """
    Отправляет запрос к OpenRouter API.
    
    Args:
        model_data: Словарь с данными модели (должен содержать api_key, api_url, name)
        prompt: Текст промта
        timeout: Таймаут запроса в секундах
        
    Returns:
        Словарь с ответом: {'response': str, 'tokens_used': int, 'response_time': float}
        
    Raises:
        APIError: При ошибке запроса
    """
    api_key = model_data.get('api_key')
    api_url = model_data.get('api_url', 'https://openrouter.ai/api/v1/chat/completions')
    
    if not api_key:
        raise APIError("API-ключ не найден. Проверьте переменную окружения 'OPENROUTER_API_KEY' в файле .env")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/chatlist",
        "X-Title": "ChatList"
    }
    
    # Определяем модель из названия
    # Название модели должно быть в формате provider/model (например, openai/gpt-4)
    model_name = model_data.get('name', 'openai/gpt-4')
    
    # Маппинг старых названий на правильные имена моделей OpenRouter
    # Актуальные названия моделей можно проверить на https://openrouter.ai/models
    # Примечание: OpenRouter не поддерживает модели Groq напрямую, используем Meta Llama
    model_name_mapping = {
        'gpt-4': 'openai/gpt-4',
        'gpt4': 'openai/gpt-4',
        'gpt-3.5': 'openai/gpt-3.5-turbo',
        'gpt-3.5-turbo': 'openai/gpt-3.5-turbo',
        'deepseek chat': 'deepseek/deepseek-chat-v3.1',
        'deepseek': 'deepseek/deepseek-chat-v3.1',
        'groq llama 3': 'meta-llama/llama-3.3-70b-instruct',
        'groq llama': 'meta-llama/llama-3.3-70b-instruct',
        'groq': 'meta-llama/llama-3.3-70b-instruct',
        'llama 3': 'meta-llama/llama-3.3-70b-instruct',
        'claude': 'anthropic/claude-3-opus',
        'gemini': 'google/gemini-pro',
        'mistral devstral': 'mistralai/devstral-2512',
        'devstral': 'mistralai/devstral-2512',
        'qwen coder': 'qwen/qwen3-coder',
        'qwen3 coder': 'qwen/qwen3-coder',
        'openai/gpt-4': 'openai/gpt-4',
        'anthropic/claude-3-opus': 'anthropic/claude-3-opus',
        'google/gemini-pro': 'google/gemini-pro',
        'meta-llama/llama-3-70b-instruct': 'meta-llama/llama-3.3-70b-instruct',
        'meta-llama/llama-3.1-70b-instruct': 'meta-llama/llama-3.3-70b-instruct',
        'groq/llama-3-70b-versatile': 'meta-llama/llama-3.3-70b-instruct',
        'groq/llama-3.1-70b-versatile': 'meta-llama/llama-3.3-70b-instruct',
        'groq/llama-3.3-70b-versatile': 'meta-llama/llama-3.3-70b-instruct',
        'deepseek/deepseek-chat': 'deepseek/deepseek-chat-v3.1',
        'mistralai/devstral-2512': 'mistralai/devstral-2512',
        'qwen/qwen3-coder': 'qwen/qwen3-coder',
    }
    
    # Нормализуем название модели
    model_name_lower = model_name.lower().strip()
    
    # Сначала проверяем точное совпадение
    if model_name_lower in model_name_mapping:
        model_name = model_name_mapping[model_name_lower]
    # Если в названии уже есть формат provider/model, проверяем, не является ли оно устаревшим
    elif '/' in model_name:
        # Проверяем устаревшие названия моделей
        if model_name_lower.startswith('groq/'):
            # OpenRouter не поддерживает Groq напрямую, используем Meta Llama
            model_name = 'meta-llama/llama-3.3-70b-instruct'
        elif 'meta-llama/llama-3' in model_name_lower and '3.3' not in model_name_lower:
            # Обновляем старые версии Llama 3 на актуальную 3.3
            model_name = 'meta-llama/llama-3.3-70b-instruct'
        elif model_name_lower == 'deepseek/deepseek-chat':
            # Обновляем старое название DeepSeek на актуальное
            model_name = 'deepseek/deepseek-chat-v3.1'
    # Если название не в формате provider/model, пробуем определить по содержимому
    else:
        # Автоматическое определение провайдера по названию
        if 'deepseek' in model_name_lower:
            # Правильное название для DeepSeek в OpenRouter
            model_name = 'deepseek/deepseek-chat-v3.1'
        elif 'groq' in model_name_lower or ('llama' in model_name_lower and 'groq' in model_name_lower):
            # OpenRouter не поддерживает Groq напрямую, используем Meta Llama 3.3
            model_name = 'meta-llama/llama-3.3-70b-instruct'
        elif 'llama' in model_name_lower:
            model_name = 'meta-llama/llama-3.3-70b-instruct'
        elif 'claude' in model_name_lower or 'anthropic' in model_name_lower:
            model_name = 'anthropic/claude-3-opus'
        elif 'gemini' in model_name_lower or 'google' in model_name_lower:
            model_name = 'google/gemini-pro'
        elif 'mistral' in model_name_lower or 'devstral' in model_name_lower:
            model_name = 'mistralai/devstral-2512'
        elif 'qwen' in model_name_lower and 'coder' in model_name_lower:
            model_name = 'qwen/qwen3-coder'
        elif 'qwen' in model_name_lower:
            model_name = 'qwen/qwen3-coder'
        elif 'gpt' in model_name_lower or 'openai' in model_name_lower:
            if '3.5' in model_name_lower or 'turbo' in model_name_lower:
                model_name = 'openai/gpt-3.5-turbo'
            else:
                model_name = 'openai/gpt-4'
        else:
            # По умолчанию используем GPT-4
            model_name = 'openai/gpt-4'
    
    payload = {
        "model": model_name,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }
    
    start_time = time.time()
    
    try:
        response = requests.post(api_url, json=payload, headers=headers, timeout=timeout)
        
        # Обрабатываем ошибки более подробно для OpenRouter
        if response.status_code == 400:
            try:
                error_data = response.json()
                error_message = error_data.get('error', {}).get('message', 'Bad Request')
                # Показываем более подробную информацию об ошибке
                detailed_error = f"Ошибка 400: {error_message}. Используемая модель: {model_name}. Оригинальное название: {model_data.get('name')}"
                logger.error(f"Ошибка запроса к {model_data.get('name')}: {detailed_error}")
                raise APIError(detailed_error)
            except (ValueError, KeyError, TypeError):
                # Если не удалось распарсить JSON с ошибкой
                error_text = response.text[:200] if hasattr(response, 'text') and response.text else 'Unknown error'
                raise APIError(f"Ошибка 400 Bad Request. Используемая модель: {model_name}. Оригинальное название: {model_data.get('name')}. Ответ сервера: {error_text}")
        
        response.raise_for_status()
        
        response_time = time.time() - start_time
        data = response.json()
        
        if 'choices' in data and len(data['choices']) > 0:
            response_text = data['choices'][0]['message']['content']
        else:
            raise APIError("Неожиданный формат ответа от API")
        
        tokens_used = None
        if 'usage' in data:
            tokens_used = data['usage'].get('total_tokens')
        
        logger.info(f"Запрос к {model_data.get('name')} (модель OpenRouter: {model_name}) выполнен за {response_time:.2f}с")
        
        return {
            'response': response_text,
            'tokens_used': tokens_used,
            'response_time': response_time
        }
        
    except APIError:
        raise
    except requests.exceptions.Timeout:
        raise APIError(f"Таймаут запроса к {model_data.get('name')}")
    except requests.exceptions.RequestException as e:
        raise APIError(f"Ошибка запроса к {model_data.get('name')}: {str(e)}")


def send_prompt_with_system_to_model(model_data: Dict, system_prompt: str, user_prompt: str, 
                                      timeout: int = 30, max_retries: int = 2) -> Dict:
    """
    Отправляет промт с системным сообщением в конкретную модель.
    
    Args:
        model_data: Словарь с данными модели (должен содержать model_type, api_key, api_url, name)
        system_prompt: Системный промт (инструкции для AI)
        user_prompt: Пользовательский промт (основной запрос)
        timeout: Таймаут запроса в секундах
        max_retries: Максимальное количество попыток при ошибке
        
    Returns:
        Словарь с ответом: {'response': str, 'tokens_used': int, 'response_time': float}
        
    Raises:
        APIError: При ошибке запроса после всех попыток
    """
    model_type = model_data.get('model_type', 'openai').lower()
    api_key = model_data.get('api_key')
    api_url = model_data.get('api_url', 'https://openrouter.ai/api/v1/chat/completions')
    
    if not api_key:
        raise APIError(f"API-ключ не найден для модели {model_data.get('name')}")
    
    # Для OpenRouter и других OpenAI-совместимых API
    if model_type == 'openrouter' or 'openrouter' in api_url.lower():
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/chatlist",
            "X-Title": "ChatList"
        }
        
        # Определяем модель из названия
        model_name = model_data.get('name', 'openai/gpt-4')
        model_name_mapping = {
            'gpt-4': 'openai/gpt-4',
            'gpt4': 'openai/gpt-4',
            'gpt-3.5': 'openai/gpt-3.5-turbo',
            'gpt-3.5-turbo': 'openai/gpt-3.5-turbo',
            'deepseek chat': 'deepseek/deepseek-chat-v3.1',
            'deepseek': 'deepseek/deepseek-chat-v3.1',
            'groq llama 3': 'meta-llama/llama-3.3-70b-instruct',
            'groq llama': 'meta-llama/llama-3.3-70b-instruct',
            'groq': 'meta-llama/llama-3.3-70b-instruct',
            'llama 3': 'meta-llama/llama-3.3-70b-instruct',
            'claude': 'anthropic/claude-3-opus',
            'gemini': 'google/gemini-pro',
        }
        
        model_name_lower = model_name.lower().strip()
        if model_name_lower in model_name_mapping:
            model_name = model_name_mapping[model_name_lower]
        elif '/' not in model_name:
            # Автоматическое определение провайдера
            if 'deepseek' in model_name_lower:
                model_name = 'deepseek/deepseek-chat-v3.1'
            elif 'llama' in model_name_lower:
                model_name = 'meta-llama/llama-3.3-70b-instruct'
            elif 'claude' in model_name_lower or 'anthropic' in model_name_lower:
                model_name = 'anthropic/claude-3-opus'
            elif 'gemini' in model_name_lower or 'google' in model_name_lower:
                model_name = 'google/gemini-pro'
            elif 'gpt' in model_name_lower:
                model_name = 'openai/gpt-4'
            else:
                model_name = 'openai/gpt-4'
        
        payload = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.7
        }
        
        last_error = None
        for attempt in range(max_retries + 1):
            try:
                start_time = time.time()
                response = requests.post(api_url, json=payload, headers=headers, timeout=timeout)
                
                if response.status_code == 400:
                    try:
                        error_data = response.json()
                        error_message = error_data.get('error', {}).get('message', 'Bad Request')
                        raise APIError(f"Ошибка 400: {error_message}. Используемая модель: {model_name}")
                    except (ValueError, KeyError, TypeError):
                        error_text = response.text[:200] if hasattr(response, 'text') and response.text else 'Unknown error'
                        raise APIError(f"Ошибка 400 Bad Request. Модель: {model_name}. Ответ: {error_text}")
                
                response.raise_for_status()
                response_time = time.time() - start_time
                data = response.json()
                
                if 'choices' in data and len(data['choices']) > 0:
                    response_text = data['choices'][0]['message']['content']
                else:
                    raise APIError("Неожиданный формат ответа от API")
                
                tokens_used = data.get('usage', {}).get('total_tokens') if 'usage' in data else None
                
                logger.info(f"Запрос к {model_data.get('name')} (модель: {model_name}) выполнен за {response_time:.2f}с")
                
                return {
                    'response': response_text,
                    'tokens_used': tokens_used,
                    'response_time': response_time
                }
                
            except APIError as e:
                last_error = e
                if attempt < max_retries:
                    wait_time = (attempt + 1) * 2
                    logger.warning(f"Попытка {attempt + 1} не удалась, повтор через {wait_time}с: {str(e)}")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Все попытки исчерпаны для {model_data.get('name')}: {str(e)}")
            except requests.exceptions.Timeout:
                last_error = APIError(f"Таймаут запроса к {model_data.get('name')}")
                if attempt < max_retries:
                    time.sleep((attempt + 1) * 2)
            except requests.exceptions.RequestException as e:
                last_error = APIError(f"Ошибка запроса к {model_data.get('name')}: {str(e)}")
                if attempt < max_retries:
                    time.sleep((attempt + 1) * 2)
        
        if last_error:
            raise last_error
        else:
            raise APIError(f"Не удалось отправить запрос к {model_data.get('name')}")
    
    else:
        # Для других типов моделей используем стандартный метод (без системного промта)
        # Объединяем системный и пользовательский промты
        combined_prompt = f"{system_prompt}\n\n---\n\n{user_prompt}"
        return send_prompt_to_model(model_data, combined_prompt, timeout, max_retries)


def send_prompt_to_model(model_data: Dict, prompt: str, timeout: int = 30, max_retries: int = 2) -> Dict:
    """
    Отправляет промт в конкретную модель с обработкой ошибок и retry-логикой.
    
    Args:
        model_data: Словарь с данными модели (должен содержать model_type, api_key, api_url, name)
        prompt: Текст промта
        timeout: Таймаут запроса в секундах
        max_retries: Максимальное количество попыток при ошибке
        
    Returns:
        Словарь с ответом: {'response': str, 'tokens_used': int, 'response_time': float}
        
    Raises:
        APIError: При ошибке запроса после всех попыток
    """
    model_type = model_data.get('model_type', 'openai').lower()
    
    last_error = None
    
    for attempt in range(max_retries + 1):
        try:
            if model_type == 'openai':
                return send_request_to_openai(model_data, prompt, timeout)
            elif model_type == 'deepseek':
                return send_request_to_deepseek(model_data, prompt, timeout)
            elif model_type == 'groq':
                return send_request_to_groq(model_data, prompt, timeout)
            elif model_type == 'openrouter':
                return send_request_to_openrouter(model_data, prompt, timeout)
            else:
                # Пробуем OpenAI-совместимый формат
                logger.warning(f"Неизвестный тип модели {model_type}, пробуем OpenAI-совместимый формат")
                return send_request_to_openai(model_data, prompt, timeout)
                
        except APIError as e:
            last_error = e
            if attempt < max_retries:
                wait_time = (attempt + 1) * 2  # Экспоненциальная задержка
                logger.warning(f"Попытка {attempt + 1} не удалась, повтор через {wait_time}с: {str(e)}")
                time.sleep(wait_time)
            else:
                logger.error(f"Все попытки исчерпаны для {model_data.get('name')}: {str(e)}")
    
    raise last_error


def send_prompt_to_multiple_models(models: List[Dict], prompt: str, 
                                   timeout: int = 30, max_workers: int = 5) -> List[Dict]:
    """
    Асинхронно отправляет промт в несколько моделей одновременно.
    
    Args:
        models: Список словарей с данными моделей
        prompt: Текст промта
        timeout: Таймаут запроса в секундах
        max_workers: Максимальное количество одновременных запросов
        
    Returns:
        Список словарей с результатами:
        [
            {
                'model_id': int,
                'model_name': str,
                'success': bool,
                'response': str (если success=True),
                'error': str (если success=False),
                'tokens_used': int,
                'response_time': float
            },
            ...
        ]
    """
    results = []
    
    def send_to_model(model):
        """Вспомогательная функция для отправки запроса к модели."""
        model_id = model.get('id')
        model_name = model.get('name', 'Unknown')
        
        try:
            response_data = send_prompt_to_model(model, prompt, timeout)
            
            return {
                'model_id': model_id,
                'model_name': model_name,
                'success': True,
                'response': response_data['response'],
                'tokens_used': response_data.get('tokens_used'),
                'response_time': response_data.get('response_time', 0)
            }
        except APIError as e:
            logger.error(f"Ошибка при запросе к {model_name}: {str(e)}")
            return {
                'model_id': model_id,
                'model_name': model_name,
                'success': False,
                'error': str(e),
                'tokens_used': None,
                'response_time': None
            }
        except Exception as e:
            logger.error(f"Неожиданная ошибка при запросе к {model_name}: {str(e)}")
            return {
                'model_id': model_id,
                'model_name': model_name,
                'success': False,
                'error': f"Неожиданная ошибка: {str(e)}",
                'tokens_used': None,
                'response_time': None
            }
    
    # Используем ThreadPoolExecutor для параллельных запросов
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_model = {executor.submit(send_to_model, model): model for model in models}
        
        for future in as_completed(future_to_model):
            result = future.result()
            results.append(result)
    
    return results

