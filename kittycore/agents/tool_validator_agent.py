"""
🔧 ToolValidatorAgent - Специалист по валидации инструментов

Единственная ответственность: проверять и исправлять названия инструментов
"""

from typing import Dict, Any, List
from dataclasses import dataclass


@dataclass 
class ToolValidationResult:
    """Результат валидации инструментов"""
    is_valid: bool
    corrected_steps: List[Dict[str, Any]]
    corrections_made: List[str]
    validation_errors: List[str]


class ToolValidatorAgent:
    """🔧 Агент-специалист по валидации инструментов"""
    
    # Строго определённые инструменты системы
    VALID_TOOLS = {
        "file_manager": "Создание, чтение, запись файлов",
        "code_generator": "Генерация Python/HTML/CSS/JS кода", 
        "web_client": "HTTP запросы, поиск в интернете",
        "system_tools": "Системные команды и операции"
    }
    
    def __init__(self):
        """Инициализация валидатора"""
        self.tool_mappings = self._build_tool_mappings()
    
    def _build_tool_mappings(self) -> Dict[str, str]:
        """Строим маппинг неправильных названий на правильные"""
        return {
            # LLM часто генерирует эти неправильные названия
            "python interpreter": "code_generator",
            "python_interpreter": "code_generator", 
            "live server": "system_tools",
            "live_server": "system_tools",
            "python editor": "code_generator",
            "python_editor": "code_generator",
            "nothing": "file_manager",
            "none": "file_manager",
            
            # Русские названия
            "файл_менеджер": "file_manager",
            "генератор_кода": "code_generator", 
            "веб_клиент": "web_client",
            "системные_инструменты": "system_tools",
            
            # Сокращения
            "file": "file_manager",
            "code": "code_generator",
            "web": "web_client",
            "system": "system_tools"
        }
    
    def validate_plan(self, plan: Dict[str, Any]) -> ToolValidationResult:
        """
        🎯 ГЛАВНЫЙ МЕТОД: Валидация плана выполнения
        
        Args:
            plan: План с шагами для валидации
            
        Returns:
            ToolValidationResult с результатами валидации и исправлениями
        """
        steps = plan.get("steps", [])
        if not steps:
            return ToolValidationResult(
                is_valid=False,
                corrected_steps=[],
                corrections_made=[],
                validation_errors=["❌ План не содержит шагов"]
            )
        
        corrected_steps = []
        corrections_made = []
        validation_errors = []
        
        print(f"🔧 Валидируем план из {len(steps)} шагов...")
        
        for i, step in enumerate(steps):
            try:
                corrected_step, correction_msg = self._validate_step(step, i + 1)
                corrected_steps.append(corrected_step)
                
                if correction_msg:
                    corrections_made.append(correction_msg)
                    print(f"   {correction_msg}")
                    
            except Exception as e:
                error_msg = f"Шаг {i+1}: {str(e)}"
                validation_errors.append(error_msg)
                print(f"   ❌ {error_msg}")
                
                # Добавляем безопасный fallback шаг
                corrected_steps.append({
                    "step": i + 1,
                    "action": step.get("action", "Выполнить действие"),
                    "tool": "file_manager",  # Самый безопасный инструмент
                    "params": step.get("params", {})
                })
                corrections_made.append(f"Шаг {i+1}: Критическая ошибка, использован file_manager")
        
        is_valid = len(validation_errors) == 0
        
        if is_valid and not corrections_made:
            print(f"✅ Все {len(steps)} инструментов валидны")
        elif corrections_made:
            print(f"🔧 Внесено {len(corrections_made)} исправлений")
        else:
            print(f"❌ План содержит {len(validation_errors)} ошибок")
        
        return ToolValidationResult(
            is_valid=is_valid,
            corrected_steps=corrected_steps,
            corrections_made=corrections_made,
            validation_errors=validation_errors
        )
    
    def _validate_step(self, step: Dict[str, Any], step_num: int) -> tuple[Dict[str, Any], str]:
        """
        Валидация одного шага
        
        Returns:
            (corrected_step, correction_message)
        """
        original_tool = step.get("tool", "")
        
        # Очистка инструмента от лишних символов
        cleaned_tool = self._clean_tool_name(original_tool)
        
        # Поиск правильного инструмента
        correct_tool = self._find_correct_tool(cleaned_tool, step)
        
        # Создаём исправленный шаг
        corrected_step = step.copy()
        corrected_step["tool"] = correct_tool
        
        # Генерируем сообщение об исправлении
        correction_msg = ""
        if original_tool != correct_tool:
            correction_msg = f"🔧 Шаг {step_num}: '{original_tool}' → '{correct_tool}'"
        
        return corrected_step, correction_msg
    
    def _clean_tool_name(self, tool_name: str) -> str:
        """Очистка названия инструмента от лишних символов"""
        if not tool_name:
            return ""
        
        # Убираем лишние символы которые часто добавляет LLM
        cleaned = tool_name.strip()
        cleaned = cleaned.replace("`", "").replace(".", "").replace('"', '').replace("'", "")
        cleaned = cleaned.replace("(", "").replace(")", "").replace("[", "").replace("]", "")
        
        # Нормализуем к нижнему регистру
        return cleaned.lower().strip()
    
    def _find_correct_tool(self, cleaned_tool: str, step: Dict[str, Any]) -> str:
        """Поиск правильного инструмента на основе названия и контекста"""
        
        # 1. Прямая проверка валидности
        if cleaned_tool in self.VALID_TOOLS:
            return cleaned_tool
        
        # 2. Поиск в маппингах
        if cleaned_tool in self.tool_mappings:
            return self.tool_mappings[cleaned_tool]
        
        # 3. Семантический анализ по действию и параметрам
        return self._semantic_tool_detection(cleaned_tool, step)
    
    def _semantic_tool_detection(self, tool_name: str, step: Dict[str, Any]) -> str:
        """Семантическое определение инструмента по контексту шага"""
        action = step.get("action", "").lower()
        params = step.get("params", {})
        
        # Анализируем действие
        if any(keyword in action for keyword in ["создать", "файл", "записать", "сохранить", "текст"]):
            # Смотрим на параметры для уточнения
            filename = params.get("filename", "")
            if filename.endswith((".py", ".html", ".js", ".css", ".json")):
                return "code_generator"
            else:
                return "file_manager"
                
        elif any(keyword in action for keyword in ["код", "скрипт", "программа", "html", "css", "js"]):
            return "code_generator"
            
        elif any(keyword in action for keyword in ["поиск", "найти", "интернет", "сайт", "анализ", "исследование"]):
            return "web_client"
            
        elif any(keyword in action for keyword in ["выполнить", "команда", "система", "запустить"]):
            return "system_tools"
        
        # Анализируем параметры
        if "filename" in params:
            filename = params["filename"]
            if filename.endswith((".py", ".html", ".js", ".css", ".json")):
                return "code_generator"
            else:
                return "file_manager"
        
        if "query" in params or "url" in params:
            return "web_client"
        
        if "command" in params:
            return "system_tools"
        
        # Fallback: самый безопасный инструмент
        return "file_manager"


def create_tool_validator() -> ToolValidatorAgent:
    """Фабричная функция для создания валидатора инструментов"""
    return ToolValidatorAgent()
