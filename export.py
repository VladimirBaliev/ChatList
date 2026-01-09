"""
Модуль для экспорта данных в различные форматы.
"""
import json
from datetime import datetime
from typing import List, Dict
import db


def export_results_to_markdown(results: List[Dict], filename: str) -> bool:
    """
    Экспортирует результаты в Markdown формат.
    
    Args:
        results: Список словарей с результатами
        filename: Имя файла для сохранения
        
    Returns:
        True если экспорт успешен
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("# Экспорт результатов ChatList\n\n")
            f.write(f"Дата экспорта: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")
            
            for i, result in enumerate(results, 1):
                f.write(f"## Результат {i}\n\n")
                f.write(f"**Дата:** {result.get('saved_at', 'N/A')}\n\n")
                f.write(f"**Модель:** {result.get('model_name', 'N/A')}\n\n")
                f.write(f"**Промт:**\n\n{result.get('prompt_text', 'N/A')}\n\n")
                f.write(f"**Ответ:**\n\n{result['response']}\n\n")
                
                if result.get('tokens_used'):
                    f.write(f"**Токенов использовано:** {result['tokens_used']}\n\n")
                if result.get('response_time'):
                    f.write(f"**Время ответа:** {result['response_time']:.2f}с\n\n")
                
                f.write("---\n\n")
        
        return True
    except Exception as e:
        raise Exception(f"Ошибка при экспорте в Markdown: {str(e)}")


def export_results_to_json(results: List[Dict], filename: str) -> bool:
    """
    Экспортирует результаты в JSON формат.
    
    Args:
        results: Список словарей с результатами
        filename: Имя файла для сохранения
        
    Returns:
        True если экспорт успешен
    """
    try:
        export_data = {
            'export_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_results': len(results),
            'results': []
        }
        
        for result in results:
            export_data['results'].append({
                'id': result.get('id'),
                'saved_at': result.get('saved_at'),
                'model_name': result.get('model_name'),
                'prompt_text': result.get('prompt_text'),
                'response': result['response'],
                'tokens_used': result.get('tokens_used'),
                'response_time': result.get('response_time')
            })
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        return True
    except Exception as e:
        raise Exception(f"Ошибка при экспорте в JSON: {str(e)}")
