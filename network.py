"""
Модуль для отправки запросов к API нейросетей.
Обрабатывает различные типы API и ошибки.
"""
import requests
import time
import logging
from typing import Dict, Optional, List
from concurrent.futures import ThreadPoolExecutor, as_completed

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


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
    # Если в названии нет провайдера, пробуем определить по типу или используем openai/
    if '/' not in model_name:
        # Если название просто "GPT-4" или подобное, добавляем openai/
        model_name = f"openai/{model_name}"
    
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

