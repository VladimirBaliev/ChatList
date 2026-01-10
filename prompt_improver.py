"""
Модуль для улучшения промтов с помощью AI-ассистента.
Использует существующий OpenRouter-клиент для отправки запросов.
"""
import json
import re
import logging
from typing import Dict, List, Optional, Tuple

import network
import models

logger = logging.getLogger(__name__)


class PromptImprovementError(Exception):
    """Исключение для ошибок улучшения промта."""
    pass


def _get_system_prompt_template(improvement_type: Optional[str] = None) -> str:
    """
    Формирует системный промт для улучшения в зависимости от типа.
    
    Args:
        improvement_type: Тип улучшения ('code', 'analysis', 'creative', None)
        
    Returns:
        Системный промт для AI-ассистента
    """
    base_prompt = """Ты - эксперт по улучшению промптов для AI-моделей. 
Твоя задача - улучшить предоставленный промпт и предложить несколько альтернативных вариантов.

ВАЖНО: Ответ должен быть в формате JSON со следующей структурой:
{
    "improved": "Улучшенная версия промпта",
    "alternatives": [
        "Альтернативный вариант 1",
        "Альтернативный вариант 2",
        "Альтернативный вариант 3"
    ]
}

Требования к улучшенной версии:
- Сохраняет основную идею и цель исходного промта
- Делает формулировку более точной и ясной
- Добавляет необходимый контекст, если его не хватает
- Исправляет грамматические и стилистические ошибки
- Оптимизирует структуру для лучшего понимания AI-моделью

Требования к альтернативным вариантам:
- Каждый вариант должен быть уникальным и предлагать другой подход
- Сохранять смысл исходного промта
- Предлагать разные способы формулировки одной и той же идеи
"""
    
    if improvement_type == 'code':
        additional = """
ДОПОЛНИТЕЛЬНО для улучшенной версии и альтернатив (фокус на код):
- Используй техническую терминологию точно и корректно
- Структурируй запрос так, чтобы AI понимал, что нужно написать код
- Четко указывай язык программирования, если это применимо
- Описывай требования к коду структурированно (входные данные, выходные данные, ограничения)
- Используй примеры кода, если это поможет уточнить задачу
"""
        return base_prompt + additional
    
    elif improvement_type == 'analysis':
        additional = """
ДОПОЛНИТЕЛЬНО для улучшенной версии и альтернатив (фокус на анализ):
- Делай запрос более детализированным и структурированным
- Четко указывай, какие аспекты нужно проанализировать
- Определяй ожидаемый формат ответа (список, таблица, структурированный текст)
- Добавляй критерии оценки или сравнения, если применимо
- Используй конкретные вопросы для направления анализа
"""
        return base_prompt + additional
    
    elif improvement_type == 'creative':
        additional = """
ДОПОЛНИТЕЛЬНО для улучшенной версии и альтернатив (фокус на креативность):
- Делай формулировку более образной и выразительной
- Добавляй контекст для творческого подхода
- Используй более живой и эмоциональный язык
- Предлагай различные стили и подходы в альтернативных вариантах
- Фокусируйся на вдохновении и оригинальности
"""
        return base_prompt + additional
    
    return base_prompt


def _format_prompt_text(text: str) -> str:
    """
    Форматирует текст промта: удаляет лишние пробелы, переносы.
    
    Args:
        text: Исходный текст
        
    Returns:
        Отформатированный текст
    """
    if not text:
        return ""
    
    # Удаляем лишние пробелы в начале и конце
    text = text.strip()
    
    # Заменяем множественные пробелы на один
    text = re.sub(r' +', ' ', text)
    
    # Удаляем множественные переносы строк (более 2 подряд)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Удаляем пробелы в начале и конце каждой строки
    lines = text.split('\n')
    lines = [line.strip() for line in lines]
    text = '\n'.join(lines)
    
    # Удаляем пустые строки в начале и конце
    text = text.strip()
    
    return text


def _parse_ai_response(response_text: str) -> Dict[str, List[str]]:
    """
    Парсит ответ от AI в структурированный формат.
    
    Обрабатывает различные форматы ответа:
    - JSON-структурированный ответ (предпочтительно)
    - Текстовый ответ с маркерами/разделителями
    - Список с нумерацией
    
    Args:
        response_text: Текст ответа от AI
        
    Returns:
        Словарь с ключами 'improved' и 'alternatives' (список строк)
        
    Raises:
        PromptImprovementError: Если не удалось распарсить ответ
    """
    response_text = response_text.strip()
    
    # Попытка 1: Парсинг JSON
    # Ищем JSON в тексте (может быть обернут в markdown код-блоки)
    json_match = re.search(r'\{[\s\S]*\}', response_text)
    if json_match:
        try:
            json_str = json_match.group(0)
            # Убираем markdown форматирование, если есть
            json_str = re.sub(r'```json\s*', '', json_str)
            json_str = re.sub(r'```\s*', '', json_str)
            json_str = json_str.strip()
            
            data = json.loads(json_str)
            
            # Валидация структуры
            if 'improved' in data and 'alternatives' in data:
                improved = _format_prompt_text(str(data['improved']))
                alternatives = data['alternatives']
                
                # Проверяем, что alternatives - это список
                if isinstance(alternatives, list):
                    alternatives = [_format_prompt_text(str(alt)) for alt in alternatives if alt]
                    alternatives = [alt for alt in alternatives if alt]  # Убираем пустые
                    return {
                        'improved': improved,
                        'alternatives': alternatives
                    }
                elif isinstance(alternatives, str):
                    # Если alternatives - строка, пытаемся разделить на список
                    alternatives = [_format_prompt_text(alt) for alt in alternatives.split('\n') if alt.strip()]
                    alternatives = [alt for alt in alternatives if alt]  # Убираем пустые
                    return {
                        'improved': improved,
                        'alternatives': alternatives
                    }
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            logger.warning(f"Не удалось распарсить JSON: {e}")
    
    # Попытка 2: Парсинг текстового формата с маркерами
    # Ищем паттерны типа "Улучшенная версия:", "Альтернатива 1:", и т.д.
    improved_patterns = [
        r'улучшенн[а-я]+ верси[яюи]:\s*\n?(.+?)(?=\n(?:альтернатив|вариант|$))',
        r'improved[:\-]?\s*\n?(.+?)(?=\n(?:alternative|variant|$))',
        r'#\s*улучшенн[а-я]+[^\n]*\n(.+?)(?=\n#|$)',
    ]
    
    alternatives_patterns = [
        r'альтернатив[а-я]+ \d+[:\-]?\s*\n?(.+?)(?=\n(?:альтернатив|вариант|$|\n\n))',
        r'вариант \d+[:\-]?\s*\n?(.+?)(?=\n(?:вариант|альтернатив|$|\n\n))',
        r'alternative \d+[:\-]?\s*\n?(.+?)(?=\n(?:alternative|variant|$|\n\n))',
        r'\d+[\.\)]\s*(.+?)(?=\n\d+[\.\)]|\n\n|$)',
    ]
    
    improved = None
    alternatives = []
    
    # Ищем улучшенную версию
    for pattern in improved_patterns:
        match = re.search(pattern, response_text, re.IGNORECASE | re.DOTALL | re.MULTILINE)
        if match:
            improved = match.group(1).strip()
            break
    
    # Ищем альтернативы
    for pattern in alternatives_patterns:
        matches = re.findall(pattern, response_text, re.IGNORECASE | re.DOTALL | re.MULTILINE)
        if matches:
            alternatives = [m.strip() for m in matches[:3] if m.strip()]  # Берем максимум 3
            break
    
    # Если не нашли через паттерны, пытаемся найти нумерованный список
    if not improved and not alternatives:
        lines = response_text.split('\n')
        potential_items = []
        for line in lines:
            line = line.strip()
            # Ищем строки, начинающиеся с числа
            if re.match(r'^\d+[\.\)\-]\s+', line):
                item = re.sub(r'^\d+[\.\)\-]\s+', '', line)
                if item:
                    potential_items.append(item)
            elif line and not line.startswith('#') and not line.startswith('*'):
                # Если строка не пустая и не является заголовком/маркером, возможно это улучшенная версия
                if not improved and len(line) > 20:  # Минимальная длина для промта
                    improved = line
                    continue
                if len(potential_items) == 0 and len(line) > 20:
                    improved = line
        
        if not improved and potential_items:
            improved = potential_items[0]
            alternatives = potential_items[1:4]  # Берем следующие 3 как альтернативы
        elif potential_items:
            alternatives = potential_items[:3]
    
    # Если все еще ничего не нашли, используем весь текст как улучшенную версию
    if not improved:
        # Разбиваем текст на параграфы
        paragraphs = [p.strip() for p in response_text.split('\n\n') if p.strip()]
        if paragraphs:
            improved = paragraphs[0]
            if len(paragraphs) > 1:
                alternatives = paragraphs[1:4]  # Следующие параграфы как альтернативы
        else:
            improved = response_text
    
    # Форматируем результаты
    if improved:
        improved = _format_prompt_text(improved)
    alternatives = [_format_prompt_text(alt) for alt in alternatives if alt]
    alternatives = [alt for alt in alternatives if alt]  # Убираем пустые
    
    # Валидация результата
    if not improved or len(improved) < 5:
        raise PromptImprovementError(
            "Не удалось извлечь улучшенную версию промта из ответа AI. "
            "Попробуйте другую модель или переформулируйте запрос."
        )
    
    # Убеждаемся, что есть хотя бы 2 альтернативы (если нет, создаем варианты на основе улучшенной)
    # Но не просто копируем, а создаем небольшие вариации
    if len(alternatives) < 2 and improved:
        # Используем улучшенную версию как первую альтернативу, если нет других
        if not alternatives or alternatives[0] != improved:
            alternatives.insert(0, improved)
        # Если все еще недостаточно, добавляем улучшенную версию еще раз
        # (в реальности это можно улучшить, создавая вариации)
        while len(alternatives) < 2:
            alternatives.append(improved)
    
    return {
        'improved': improved,
        'alternatives': alternatives[:3]  # Максимум 3 альтернативы
    }


def improve_prompt(
    original_prompt: str, 
    model_id: int, 
    improvement_type: Optional[str] = None
) -> Dict[str, List[str]]:
    """
    Улучшает промт с помощью AI-ассистента.
    
    Args:
        original_prompt: Исходный текст промта от пользователя
        model_id: Идентификатор модели из БД для отправки запроса
        improvement_type: Тип улучшения ('code', 'analysis', 'creative', None)
        
    Returns:
        Словарь с ключами:
        - 'improved': str - улучшенная версия промта
        - 'alternatives': List[str] - список из 2-3 альтернативных вариантов
        
    Raises:
        PromptImprovementError: При ошибке улучшения промта
    """
    if not original_prompt or not original_prompt.strip():
        raise PromptImprovementError("Исходный промт не может быть пустым")
    
    # Валидация типа улучшения
    if improvement_type and improvement_type not in ['code', 'analysis', 'creative']:
        logger.warning(f"Неизвестный тип улучшения: {improvement_type}, используем общее улучшение")
        improvement_type = None
    
    # Получаем модель с API-ключом
    model_data = models.ModelManager.get_model_with_key(model_id)
    if not model_data:
        raise PromptImprovementError(f"Модель с ID {model_id} не найдена в БД")
    
    if not model_data.get('api_key'):
        raise PromptImprovementError(
            f"API-ключ не найден для модели {model_data.get('name')}. "
            "Проверьте переменную окружения OPENROUTER_API_KEY в файле .env"
        )
    
    # Формируем системный промт
    system_prompt = _get_system_prompt_template(improvement_type)
    
    # Формируем пользовательский промт
    user_prompt = f"""Исходный промт, который нужно улучшить:

{original_prompt}

Пожалуйста, улучши этот промт и предложи несколько альтернативных вариантов в формате JSON, как указано в системном промпте."""
    
    # Отправляем запрос через существующий network модуль
    try:
        logger.info(f"Отправка запроса на улучшение промта в модель {model_data.get('name')}")
        
        # Используем функцию send_prompt_with_system_to_model для правильной отправки
        # системного и пользовательского промтов отдельно
        response_data = network.send_prompt_with_system_to_model(
            model_data, 
            system_prompt,
            user_prompt,
            timeout=60  # Увеличиваем таймаут для более сложных запросов
        )
        
        response_text = response_data.get('response', '')
        if not response_text:
            raise PromptImprovementError("Получен пустой ответ от AI")
        
        # Парсим ответ
        result = _parse_ai_response(response_text)
        
        logger.info("Промт успешно улучшен")
        return result
        
    except network.APIError as e:
        error_msg = f"Ошибка API при улучшении промта: {str(e)}"
        logger.error(error_msg)
        raise PromptImprovementError(error_msg)
    except Exception as e:
        error_msg = f"Неожиданная ошибка при улучшении промта: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise PromptImprovementError(error_msg)

