import re
import json # Добавил, т.к. может понадобиться для логов или работы с контекстом
from typing import Dict, Any, List # List добавлен для resolve_string_template и _resolve_value_from_context
from loguru import logger # Для логирования внутри функций

# Скопировано из app.core.scenario_executor
def _resolve_value_from_context(value: Any, context: Dict[str, Any], depth=0, max_depth=10) -> Any:
    if depth > max_depth:
        logger.warning(f"Max recursion depth reached in _resolve_value_from_context for value: {value}")
        return value

    if isinstance(value, str):
        if value.startswith("{") and value.endswith("}"):
            key_path = value[1:-1]
            parts = key_path.split('.')
            current_value = context
            resolved_successfully = True
            for part in parts:
                if isinstance(current_value, dict) and part in current_value:
                    current_value = current_value[part]
                elif isinstance(current_value, list): 
                    try:
                        idx = int(part)
                        if 0 <= idx < len(current_value):
                            current_value = current_value[idx]
                        else:
                            resolved_successfully = False
                            break
                    except ValueError:
                        resolved_successfully = False
                        break
                else:
                    resolved_successfully = False
                    break
            
            if resolved_successfully:
                # Рекурсивный вызов для случаев, когда значение из контекста само является плейсхолдером
                if isinstance(current_value, str) and current_value.startswith("{") and current_value.endswith("}") and current_value != value:
                    return _resolve_value_from_context(current_value, context, depth + 1, max_depth)
                return current_value
            else: # Если прямой резолвинг по ключу не удался, пытаемся как шаблон строки
                return resolve_string_template(value, context) # Используем resolve_string_template для обработки строк с несколькими плейсхолдерами или текстом вокруг
        else:
            # Если строка не похожа на одиночный плейсхолдер {key.path}, все равно пытаемся обработать ее как шаблон
            return resolve_string_template(value, context)

    elif isinstance(value, dict):
        return {k: _resolve_value_from_context(v, context, depth + 1, max_depth) for k, v in value.items()}
    elif isinstance(value, list):
        return [_resolve_value_from_context(item, context, depth + 1, max_depth) for item in value]
    return value

# Скопировано из app.core.scenario_executor
def resolve_string_template(template_str: str, ctx: Dict[str, Any]) -> str:
    """Разрешает плейсхолдеры в строке, включая вычисление выражений"""
    if not isinstance(template_str, str):
        return str(template_str)
        
    placeholders = re.findall(r"\{([^{}]+)\}", template_str)
    resolved_str = template_str
    
    for placeholder in placeholders:
        key_path = placeholder.strip()
        
        try:
            # Сначала пробуем простую подстановку переменной
            if key_path in ctx:
                replacement_value = str(ctx[key_path])
                resolved_str = resolved_str.replace(f"{{{placeholder}}}", replacement_value)
                continue
            
            # Если не найдена прямая переменная, пробуем путь через точки
            parts = key_path.split('.')
            current_value = ctx
            resolved_successfully = True
            
            for part in parts:
                if isinstance(current_value, dict) and part in current_value:
                    current_value = current_value[part]
                elif isinstance(current_value, list):
                    try:
                        idx = int(part)
                        if 0 <= idx < len(current_value):
                            current_value = current_value[idx]
                        else:
                            resolved_successfully = False
                            break
                    except ValueError:
                        resolved_successfully = False
                        break
                else:
                    resolved_successfully = False
                    break
            
            if resolved_successfully:
                replacement_value = str(current_value)
                resolved_str = resolved_str.replace(f"{{{placeholder}}}", replacement_value)
                continue
            
            # Если простая подстановка не удалась, пробуем вычислить как выражение
            safe_context = {}
            for key, value in ctx.items():
                if not key.startswith("__"):  # Пропускаем служебные переменные
                    safe_context[key] = value
            
            # Безопасное вычисление выражений
            result = eval(key_path, {"__builtins__": {}}, safe_context)
            replacement_value = str(result)
            resolved_str = resolved_str.replace(f"{{{placeholder}}}", replacement_value)
            logger.debug(f"🧮 Вычислено выражение в строке '{key_path}' = {result}")
            
        except Exception as e:
            logger.warning(f"⚠️ Не удалось разрешить плейсхолдер '{key_path}' в строке: {e}")
            # Если вычисление не удалось, оставляем плейсхолдер как есть
            
    return resolved_str 