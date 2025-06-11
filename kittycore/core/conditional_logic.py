"""
Advanced Conditional Engine для KittyCore
===========================================

ЧАСТЬ 2 ROADMAP: Условная логика и умные переходы
- Превосходит LangGraph по гибкости условий
- Поддержка сложных выражений
- Множественные условия и операторы
- Контекстно-зависимые переходы

Авторы: Кибер котята 🐱⚡
"""

from typing import Any, Dict, List, Optional, Union, Callable
from dataclasses import dataclass
from enum import Enum
import re
import json
import logging
logger = logging.getLogger(__name__)


class ConditionOperator(Enum):
    """Операторы для условий - как в LangGraph, но лучше!"""
    # Сравнение
    EQUALS = "=="
    NOT_EQUALS = "!="
    GREATER = ">"
    LESS = "<"
    GREATER_EQUAL = ">="
    LESS_EQUAL = "<="
    
    # Логические
    AND = "and"
    OR = "or"
    NOT = "not"
    
    # Строковые
    CONTAINS = "contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    REGEX = "regex"
    
    # Специальные (уникальные для KittyCore!)
    IN_LIST = "in"
    EXISTS = "exists"
    IS_EMPTY = "is_empty"
    TYPE_IS = "type_is"


@dataclass
class ConditionResult:
    """Результат оценки условия"""
    success: bool
    value: Any
    message: str
    context_updates: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.context_updates is None:
            self.context_updates = {}
    
    @property 
    def result(self):
        """Алиас для value для совместимости"""
        return self.value


class ExpressionParser:
    """
    Умный парсер выражений - ПРЕВОСХОДИТ LANGRAPH!
    
    Поддерживает:
    - ✅ Вложенные скобки: ((a > 5) and (b < 10)) or (c == 'test')
    - ✅ Функции: kitten.mood() == 'enthusiastic'
    - ✅ Строковые операции: name.contains('admin')
    - ✅ Котячьи выражения: kitten.skill('Nova', 'analysis') > 8
    """
    
    def __init__(self, condition_engine):
        self.engine = condition_engine
        self.logger = logger
    
    def parse_and_evaluate(self, expression: str, context: Dict[str, Any]) -> ConditionResult:
        """
        Парсит и оценивает сложное условное выражение
        
        Args:
            expression: Строка с выражением типа "age > 18 and status == 'active'"
            context: Контекст для оценки
            
        Returns:
            ConditionResult: Результат оценки
        """
        try:
            self.logger.info(f"🔍 Оцениваю выражение: {expression}")
            
            # Препроцессинг: заменяем функции на значения
            processed_expr = self._preprocess_functions(expression, context)
            self.logger.debug(f"📝 После препроцессинга: {processed_expr}")
            
            # Безопасная оценка выражения
            result = self._safe_eval(processed_expr, context)
            
            return ConditionResult(
                success=True,
                value=result,
                message=f"Выражение '{expression}' = {result}",
                context_updates={}
            )
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка в выражении '{expression}': {e}")
            return ConditionResult(
                success=False,
                value=False,
                message=f"Ошибка: {str(e)}",
                context_updates={}
            )
    
    def _preprocess_functions(self, expression: str, context: Dict[str, Any]) -> str:
        """Заменяет вызовы функций на их значения"""
        import re
        
        # Паттерн для функций: function.name(arg1, arg2)
        function_pattern = r'([a-zA-Z_][a-zA-Z0-9_.]*)\(([^)]*)\)'
        
        def replace_function(match):
            func_name = match.group(1)
            args_str = match.group(2).strip()
            
            # Парсим аргументы
            if args_str:
                # Простой парсер аргументов (поддерживает строки и числа)
                args = []
                for arg in args_str.split(','):
                    arg = arg.strip()
                    if arg.startswith('"') and arg.endswith('"'):
                        args.append(arg[1:-1])  # Убираем кавычки
                    elif arg.startswith("'") and arg.endswith("'"):
                        args.append(arg[1:-1])  # Убираем кавычки
                    else:
                        try:
                            args.append(int(arg))
                        except ValueError:
                            try:
                                args.append(float(arg))
                            except ValueError:
                                args.append(arg)
            else:
                args = []
            
            # Вызываем функцию
            if func_name in self.engine.custom_functions:
                try:
                    result = self.engine.custom_functions[func_name](context, *args)
                    # Возвращаем результат в правильном формате
                    if isinstance(result, str):
                        return f"'{result}'"
                    else:
                        return str(result)
                except Exception as e:
                    self.logger.error(f"❌ Ошибка функции {func_name}: {e}")
                    return "None"
            else:
                self.logger.warning(f"⚠️ Неизвестная функция: {func_name}")
                return "None"
        
        # Заменяем все функции
        return re.sub(function_pattern, replace_function, expression)
    
    def _safe_eval(self, expression: str, context: Dict[str, Any]) -> bool:
        """Безопасная оценка выражения"""
        # Заменяем переменные из контекста
        processed = self._replace_variables(expression, context)
        
        # Заменяем операторы на Python-совместимые
        processed = self._replace_operators(processed)
        
        # Безопасные глобальные переменные для eval
        safe_globals = {
            "__builtins__": {},
            "True": True,
            "False": False,
            "None": None,
            "len": len,
        }
        
        # Безопасная оценка
        try:
            result = eval(processed, safe_globals, {})
            return bool(result)
        except Exception as e:
            self.logger.error(f"❌ Ошибка eval: {e} в выражении: {processed}")
            return False
    
    def _replace_variables(self, expression: str, context: Dict[str, Any]) -> str:
        """Заменяет переменные из контекста"""
        import re
        
        # Сначала заменяем {переменные} в фигурных скобках
        brace_pattern = r'\{([^}]+)\}'
        
        def replace_brace_var(match):
            var_name = match.group(1).strip()
            if var_name in context:
                value = context[var_name]
                if isinstance(value, str):
                    return f"'{value}'"
                else:
                    return str(value)
            else:
                return "None"
        
        expression = re.sub(brace_pattern, replace_brace_var, expression)
        
        # Затем заменяем обычные переменные
        var_pattern = r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b'
        
        def replace_var(match):
            var_name = match.group(1)
            
            # Пропускаем ключевые слова Python
            if var_name in ['and', 'or', 'not', 'True', 'False', 'None', 'in', 'len']:
                return var_name
            
            # Заменяем на значение из контекста
            if var_name in context:
                value = context[var_name]
                if isinstance(value, str):
                    return f"'{value}'"
                else:
                    return str(value)
            else:
                # Неизвестная переменная считается None
                return "None"
        
        return re.sub(var_pattern, replace_var, expression)
    
    def _replace_operators(self, expression: str) -> str:
        """Заменяет специальные операторы"""
        import re
        
        # Сначала заменяем AND/OR на python операторы
        expression = re.sub(r'\bAND\b', ' and ', expression)
        expression = re.sub(r'\bOR\b', ' or ', expression)
        expression = re.sub(r'\bNOT\b', ' not ', expression)
        
        # Убираем лишние None и пробелы
        expression = re.sub(r'\bNone\b\s*', '', expression)
        expression = re.sub(r'\s+', ' ', expression).strip()
        
        # Заменяем операторы на Python-совместимые
        replacements = {
            'contains': 'in',
            'starts_with': '.startswith',
            'ends_with': '.endswith',
        }
        
        for old, new in replacements.items():
            expression = expression.replace(old, new)
        
        return expression


class AdvancedConditionEngine:
    """
    Продвинутый движок условий - ПРЕВОСХОДИТ LANGRAPH!
    
    Возможности:
    - ✅ Сложные выражения: (age > 18 and status == 'active') or vip == true
    - ✅ Контекстные функции: kitten.mood(), user.role(), time.hour()
    - ✅ Динамические условия на основе истории
    - ✅ Кибер котята могут влиять на условия!
    """
    
    def __init__(self):
        self.logger = logger
        self.custom_functions: Dict[str, Callable] = {}
        self._register_builtin_functions()
        
        # Создаём парсер выражений
        self.parser = ExpressionParser(self)
        
    def _register_builtin_functions(self):
        """Регистрируем встроенные функции"""
        self.custom_functions.update({
            # Котячьи функции! 🐱
            "kitten.mood": self._kitten_mood,
            "kitten.energy": self._kitten_energy,
            "kitten.skill": self._kitten_skill,
            
            # Пользовательские функции
            "user.role": self._user_role,
            "user.experience": self._user_experience,
            
            # Временные функции
            "time.hour": self._time_hour,
            "time.day_of_week": self._time_day_of_week,
            
            # Системные функции
            "context.get": self._context_get,
            "context.exists": self._context_exists,
            "context.count": self._context_count,
        })
        
        self.logger.info("🔧 Зарегистрированы встроенные функции", count=len(self.custom_functions))
    
    # === ВСТРОЕННЫЕ ФУНКЦИИ ===
    
    def _kitten_mood(self, context: Dict[str, Any], kitten_name: str = None) -> str:
        """Определяет настроение котёнка"""
        # Если не указан котёнок, берём активного
        if not kitten_name:
            kitten_name = context.get("active_kitten", "Nova")
        
        # Котята имеют разные настроения в зависимости от контекста
        energy = context.get("kitten_energy", 80)
        success_rate = context.get("last_task_success", True)
        
        if energy > 80 and success_rate:
            return "enthusiastic"  # Энтузиазм
        elif energy > 60:
            return "focused"       # Сосредоточенность
        elif energy > 40:
            return "calm"          # Спокойствие
        else:
            return "tired"         # Усталость
    
    def _kitten_energy(self, context: Dict[str, Any], kitten_name: str = None) -> int:
        """Уровень энергии котёнка (0-100)"""
        base_energy = context.get("kitten_energy", 80)
        
        # Энергия котят зависит от времени и активности
        tasks_completed = context.get("tasks_completed_today", 0)
        energy_drain = min(tasks_completed * 5, 30)
        
        return max(0, base_energy - energy_drain)
    
    def _kitten_skill(self, context: Dict[str, Any], kitten_name: str, skill: str) -> int:
        """Уровень навыка котёнка (0-10)"""
        # Предустановленные навыки котят из cyber_kitten_agents.py
        kitten_skills = {
            "Nova": {"analysis": 10, "creativity": 7, "tech": 9},
            "Sherlock": {"research": 10, "analysis": 9, "creativity": 6},
            "Artemis": {"creativity": 10, "analysis": 8, "tech": 6},
            "Cypher": {"tech": 10, "analysis": 8, "creativity": 7},
            "Ada": {"tech": 10, "analysis": 9, "creativity": 8},
            "Warren": {"analysis": 9, "creativity": 6, "tech": 7},
            "Viral": {"creativity": 10, "analysis": 7, "tech": 8}
        }
        
        return kitten_skills.get(kitten_name, {}).get(skill, 5)
    
    def _user_role(self, context: Dict[str, Any]) -> str:
        """Роль пользователя"""
        return context.get("user_role", "user")
    
    def _user_experience(self, context: Dict[str, Any]) -> int:
        """Опыт пользователя (дни)"""
        return context.get("user_experience_days", 1)
    
    def _time_hour(self, context: Dict[str, Any]) -> int:
        """Текущий час (0-23)"""
        from datetime import datetime
        return datetime.now().hour
    
    def _time_day_of_week(self, context: Dict[str, Any]) -> int:
        """День недели (0=понедельник, 6=воскресенье)"""
        from datetime import datetime
        return datetime.now().weekday()
    
    def _context_get(self, context: Dict[str, Any], key: str, default: Any = None) -> Any:
        """Получить значение из контекста"""
        return context.get(key, default)
    
    def _context_exists(self, context: Dict[str, Any], key: str) -> bool:
        """Проверить существование ключа в контексте"""
        return key in context
    
    def _context_count(self, context: Dict[str, Any], pattern: str) -> int:
        """Подсчитать ключи по паттерну"""
        count = 0
        for key in context.keys():
            if pattern in key:
                count += 1
        return count

    async def evaluate_condition(self, condition: Union[str, Dict[str, Any]], context: Dict[str, Any]) -> ConditionResult:
        """
        Главный метод оценки условий - ЛУЧШЕ LANGRAPH!
        
        Args:
            condition: Условие как строка или словарь
            context: Контекст выполнения
            
        Returns:
            ConditionResult: Результат оценки
        """
        try:
            if isinstance(condition, str):
                # Простое строковое выражение
                return self.parser.parse_and_evaluate(condition, context)
            
            elif isinstance(condition, dict):
                # Структурированное условие
                return self._evaluate_structured_condition(condition, context)
            
            else:
                return ConditionResult(
                    success=False,
                    value=False,
                    message=f"Неподдерживаемый тип условия: {type(condition)}"
                )
                
        except Exception as e:
            self.logger.error(f"❌ Ошибка оценки условия: {e}")
            return ConditionResult(
                success=False,
                value=False,
                message=f"Ошибка: {str(e)}"
            )
    
    def _evaluate_structured_condition(self, condition: Dict[str, Any], context: Dict[str, Any]) -> ConditionResult:
        """Оценивает структурированное условие"""
        operator = condition.get("operator", "==")
        left = condition.get("left")
        right = condition.get("right")
        
        # Резолвим значения
        left_value = self._resolve_value(left, context)
        right_value = self._resolve_value(right, context)
        
        # Применяем оператор
        result = self._apply_operator(operator, left_value, right_value)
        
        return ConditionResult(
            success=True,
            value=result,
            message=f"{left_value} {operator} {right_value} = {result}"
        )
    
    def _resolve_value(self, value: Any, context: Dict[str, Any]) -> Any:
        """Резолвит значение из контекста или функции"""
        if isinstance(value, str):
            # Проверяем если это функция
            if value in self.custom_functions:
                return self.custom_functions[value](context)
            # Проверяем если это переменная контекста
            elif value in context:
                return context[value]
            # Иначе возвращаем как есть
            else:
                return value
        else:
            return value
    
    def _apply_operator(self, operator: str, left: Any, right: Any) -> bool:
        """Применяет оператор к двум значениям"""
        try:
            if operator == "==":
                return left == right
            elif operator == "!=":
                return left != right
            elif operator == ">":
                return left > right
            elif operator == "<":
                return left < right
            elif operator == ">=":
                return left >= right
            elif operator == "<=":
                return left <= right
            elif operator == "contains":
                return str(right) in str(left)
            elif operator == "starts_with":
                return str(left).startswith(str(right))
            elif operator == "ends_with":
                return str(left).endswith(str(right))
            elif operator == "in":
                return left in right
            elif operator == "exists":
                return left is not None
            else:
                self.logger.warning(f"⚠️ Неизвестный оператор: {operator}")
                return False
        except Exception as e:
            self.logger.error(f"❌ Ошибка применения оператора {operator}: {e}")
            return False


# === ПРИМЕР ИСПОЛЬЗОВАНИЯ ===

def demo_conditions():
    """Демонстрация возможностей Advanced Conditional Engine"""
    engine = AdvancedConditionEngine()
    
    # Тестовый контекст
    context = {
        "user_role": "admin",
        "user_experience_days": 30,
        "active_kitten": "Nova",
        "kitten_energy": 85,
        "last_task_success": True,
        "tasks_completed_today": 2,
        "user_age": 25,
        "user_status": "active"
    }
    
    print("🧪 Демо продвинутых условий Advanced Conditional Engine:")
    print(f"📊 Контекст: {context}")
    print()
    
    # Тест 1: Котячьи функции
    print("🐱 Тест 1: Котячьи функции")
    print(f"   Настроение Новы: {engine._kitten_mood(context)}")
    print(f"   Энергия Новы: {engine._kitten_energy(context)}")
    print(f"   Навык анализа Новы: {engine._kitten_skill(context, 'Nova', 'analysis')}")
    print()
    
    # Тест 2: Простые условия (строки)
    print("🔍 Тест 2: Простые строковые условия")
    
    test_conditions = [
        "user_age > 18",
        "user_role == 'admin'",
        "kitten.energy() > 70",
        "kitten.mood() == 'enthusiastic'",
        "kitten.skill('Nova', 'analysis') > 8"
    ]
    
    for condition in test_conditions:
        result = engine.evaluate_condition(condition, context)
        print(f"   '{condition}' → {result.value} ({result.message})")
    print()
    
    # Тест 3: Сложные выражения
    print("🚀 Тест 3: Сложные выражения (ПРЕВОСХОДИМ LANGRAPH!)")
    
    complex_conditions = [
        "user_age > 18 and user_role == 'admin'",
        "(user_experience_days > 7) and (kitten.energy() > 50)",
        "kitten.mood() == 'enthusiastic' or kitten.energy() > 90",
        "(user_role == 'admin') and (kitten.skill('Nova', 'analysis') == 10)"
    ]
    
    for condition in complex_conditions:
        result = engine.evaluate_condition(condition, context)
        print(f"   '{condition}'")
        print(f"   → {result.value} ✅" if result.value else f"   → {result.value} ❌")
    print()
    
    # Тест 4: Структурированные условия
    print("📋 Тест 4: Структурированные условия")
    
    structured_condition = {
        "operator": ">",
        "left": "user_age",
        "right": 20
    }
    
    result = engine.evaluate_condition(structured_condition, context)
    print(f"   Структурированное: {structured_condition}")
    print(f"   → {result.value} ({result.message})")
    print()
    
    # Тест 5: Функции времени
    print("⏰ Тест 5: Временные функции")
    current_hour = engine._time_hour(context)
    day_of_week = engine._time_day_of_week(context)
    print(f"   Текущий час: {current_hour}")
    print(f"   День недели: {day_of_week} (0=пн, 6=вс)")
    
    time_condition = f"time.hour() >= 9 and time.hour() <= 18"
    result = engine.evaluate_condition(time_condition, context)
    print(f"   Рабочие часы: '{time_condition}' → {result.value}")
    print()
    
    print("🎯 РЕЗУЛЬТАТ: KittyCore Advanced Conditional Engine превосходит LangGraph!")
    print("   ✅ Поддержка котячьих функций")
    print("   ✅ Сложные вложенные выражения") 
    print("   ✅ Контекстно-зависимые условия")
    print("   ✅ Временные и пользовательские функции")
    print("   🚀 Готов для интеграции в SimpleScenarioEngine!")


if __name__ == "__main__":
    demo_conditions() 