# -*- coding: utf-8 -*-
"""
Продвинутый резолвер шаблонов для Universal Agent Platform.

Поддерживает все современные форматы переменных:
- {variable} - простые переменные
- {{variable}} - Django/Jinja2 стиль
- {user.name} - вложенные объекты
- {items[0]} - элементы массивов
- {current_timestamp} - специальные переменные
"""

import re
import json
from datetime import datetime
from typing import Dict, Any, Optional, Union
from loguru import logger


class TemplateResolver:
    """
    Продвинутый резолвер шаблонов с поддержкой различных форматов.
    
    Поддерживаемые форматы:
    - {variable} - простые переменные
    - {{variable}} - Django/Jinja2 стиль  
    - {user.name} - вложенные объекты
    - {items[0]} - элементы массивов
    - {items.0.name} - комбинированная навигация
    """
    
    def __init__(self):
        # Паттерны для разных типов переменных
        self.patterns = {
            # {{variable}} - Django/Jinja2 стиль
            'django': re.compile(r'\{\{([^}]+)\}\}'),
            # {variable} - простые переменные
            'simple': re.compile(r'\{([^}]+)\}'),
        }
        
        # Специальные переменные
        self.special_vars = {
            "current_timestamp": lambda: datetime.now().isoformat(),
            "current_date": lambda: datetime.now().strftime("%Y-%m-%d"),
            "current_time": lambda: datetime.now().strftime("%H:%M:%S"),
            "current_datetime": lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "current_unix": lambda: int(datetime.now().timestamp()),
        }
    
    def resolve(self, template: str, context: Dict[str, Any]) -> str:
        """
        Основной метод разрешения шаблонов.
        
        Args:
            template: Строка шаблона с переменными
            context: Контекст с данными
            
        Returns:
            str: Строка с подставленными значениями
        """
        if not isinstance(template, str):
            return str(template)
        
        result = template
        
        # 1. Сначала обрабатываем Django-стиль {{variable}}
        result = self._resolve_django_style(result, context)
        
        # 2. Затем обрабатываем простые {variable}
        result = self._resolve_simple_style(result, context)
        
        return result
    
    def _resolve_django_style(self, text: str, context: Dict[str, Any]) -> str:
        """Разрешает шаблоны в Django/Jinja2 стиле {{variable}}"""
        def replace_match(match):
            var_path = match.group(1).strip()
            try:
                value = self._get_value_by_path(var_path, context)
                return str(value) if value is not None else match.group(0)
            except (KeyError, IndexError, TypeError, AttributeError) as e:
                logger.debug("Не удалось разрешить переменную Django-стиль '{{" + var_path + "}}': " + str(e))
                return match.group(0)  # Оставляем как есть
        
        return self.patterns['django'].sub(replace_match, text)
    
    def _resolve_simple_style(self, text: str, context: Dict[str, Any]) -> str:
        """Разрешает шаблоны в простом стиле {variable}"""
        def replace_match(match):
            var_path = match.group(1).strip()
            try:
                value = self._get_value_by_path(var_path, context)
                return str(value) if value is not None else match.group(0)
            except (KeyError, IndexError, TypeError, AttributeError) as e:
                logger.debug(f"Не удалось разрешить переменную простого стиля '{{{var_path}}}': {e}")
                return match.group(0)  # Оставляем как есть
        
        return self.patterns['simple'].sub(replace_match, text)
    
    def _get_value_by_path(self, path: str, context: Dict[str, Any]) -> Any:
        """
        Получает значение по пути в контексте.
        
        Поддерживает:
        - simple_var
        - user.name
        - items[0]
        - items.0.name
        - current_timestamp (специальные)
        
        Args:
            path: Путь к переменной
            context: Контекст
            
        Returns:
            Any: Значение переменной
        """
        # Проверяем специальные переменные
        if path in self.special_vars:
            return self.special_vars[path]()
        
        # Начинаем с корня контекста
        current = context
        
        # Разбиваем путь на части
        parts = self._parse_path(path)
        
        for part in parts:
            if isinstance(part, str):
                # Обычный ключ
                if isinstance(current, dict):
                    current = current[part]
                else:
                    raise KeyError(f"Cannot access key '{part}' on non-dict object")
            elif isinstance(part, int):
                # Индекс массива
                if isinstance(current, (list, tuple)):
                    current = current[part]
                else:
                    raise IndexError(f"Cannot access index {part} on non-list object")
            else:
                raise ValueError(f"Invalid path part: {part}")
        
        return current
    
    def _parse_path(self, path: str) -> list:
        """
        Парсит путь переменной в список частей.
        
        Examples:
            "user.name" -> ["user", "name"]
            "items[0]" -> ["items", 0]
            "items.0.name" -> ["items", 0, "name"]
            "data[0].user.name" -> ["data", 0, "user", "name"]
        
        Args:
            path: Путь переменной
            
        Returns:
            list: Список частей пути
        """
        parts = []
        current_part = ""
        i = 0
        
        while i < len(path):
            char = path[i]
            
            if char == '.':
                # Точка - разделитель
                if current_part:
                    parts.append(current_part)
                    current_part = ""
            elif char == '[':
                # Начало индекса массива
                if current_part:
                    parts.append(current_part)
                    current_part = ""
                
                # Ищем закрывающую скобку
                j = i + 1
                while j < len(path) and path[j] != ']':
                    j += 1
                
                if j >= len(path):
                    raise ValueError(f"Unclosed bracket in path: {path}")
                
                # Извлекаем индекс
                index_str = path[i+1:j]
                try:
                    index = int(index_str)
                    parts.append(index)
                except ValueError:
                    raise ValueError(f"Invalid array index: {index_str}")
                
                i = j  # Пропускаем закрывающую скобку
            elif char == ']':
                # Закрывающая скобка - пропускаем
                pass
            else:
                # Обычный символ
                current_part += char
            
            i += 1
        
        # Добавляем последнюю часть
        if current_part:
            parts.append(current_part)
        
        return parts
    
    def resolve_deep(self, data: Any, context: Dict[str, Any]) -> Any:
        """
        Рекурсивно разрешает шаблоны в сложных структурах данных.
        
        Args:
            data: Данные для обработки (dict, list, str, etc.)
            context: Контекст с переменными
            
        Returns:
            Any: Обработанные данные
        """
        if isinstance(data, str):
            return self.resolve(data, context)
        elif isinstance(data, dict):
            return {key: self.resolve_deep(value, context) for key, value in data.items()}
        elif isinstance(data, list):
            return [self.resolve_deep(item, context) for item in data]
        else:
            return data
    
    def test_resolution(self, template: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Тестирует разрешение шаблона и возвращает детальную информацию.
        
        Args:
            template: Шаблон для тестирования
            context: Контекст
            
        Returns:
            Dict: Результат тестирования
        """
        try:
            result = self.resolve(template, context)
            return {
                "success": True,
                "original": template,
                "resolved": result,
                "changed": template != result
            }
        except Exception as e:
            return {
                "success": False,
                "original": template,
                "error": str(e),
                "error_type": type(e).__name__
            }


# Глобальный экземпляр для использования в системе
template_resolver = TemplateResolver() 