#!/usr/bin/env python3
"""
Умный валидатор сценариев с автоисправлением
Автоматически заменяет неподдерживаемые типы шагов на похожие поддерживаемые
"""

import yaml
import json
import requests
from typing import Dict, List, Any, Tuple
from difflib import SequenceMatcher
import sys
import argparse
from pathlib import Path
import copy

# Мапинг распространенных неправильных типов на правильные
STEP_TYPE_MAPPING = {
    # Старые/неправильные типы -> правильные типы
    "set_context": "action",
    "update_context": "action", 
    "conditional_execute": "branch",
    "condition": "branch",
    "telegram_send_message": "channel_action",
    "telegram_edit_message": "channel_action",
    "telegram_send_buttons": "channel_action",
    "send_message": "channel_action",
    "edit_message": "channel_action",
    "send_buttons": "channel_action",
    "copy_message": "channel_action",
    "forward_message": "channel_action",
    "wait_for_input": "input",
    "user_input": "input", 
    "get_input": "input",
    "text_input": "input_text",
    "button_input": "input_button",
    "save_data": "mongo_upsert_document",
    "store_data": "mongo_upsert_document",
    "find_data": "mongo_find_documents",
    "query_data": "mongo_find_documents",
    "update_data": "mongo_update_document",
    "delete_data": "mongo_delete_document",
    "create_contact": "amocrm_create_contact",
    "find_contact": "amocrm_find_contact",
    "create_lead": "amocrm_create_lead",
    "ai_query": "llm_query",
    "llm_request": "llm_query",
    "chatgpt": "llm_query",
    "openai": "llm_query",
    "search": "rag_search",
    "vector_search": "rag_search",
    "http_call": "http_request",
    "api_call": "http_request",
    "rest_call": "http_request",
    "log": "log_message",
    "print": "log_message",
    "debug": "log_message",
    "generate_pdf": "pdf_generate",
    "create_pdf": "pdf_generate",
    "route": "route_callback",
    "redirect": "route_to_step",
    "goto": "route_to_step",
    "jump": "route_to_step",
}

# Мапинг неправильных action'ов на правильные
ACTION_MAPPING = {
    "update_context": None,  # Убираем action, оставляем только обновление контекста
    "set_context": None,     # Убираем action, оставляем только обновление контекста
    "store_context": None,   # Убираем action, оставляем только обновление контекста
}

class ScenarioValidator:
    def __init__(self, api_base_url: str = "http://localhost:8085"):
        self.api_base_url = api_base_url
        self.supported_handlers = self._get_supported_handlers()
        self.fixes_applied = []
        
    def _get_supported_handlers(self) -> List[str]:
        """Получает список поддерживаемых handlers из API"""
        # ИСПРАВЛЕНО: Убираем HTTP запрос к API чтобы избежать циклической зависимости
        # try:
        #     response = requests.get(f"{self.api_base_url}/api/v1/simple/info")
        #     if response.status_code == 200:
        #         data = response.json()
        #         return data.get("registered_handlers", [])
        # except Exception as e:
        #     print(f"⚠️ Не удалось получить список handlers из API: {e}")
            
        # Используем фиксированный список поддерживаемых handlers
        return [
            "start", "end", "action", "input", "input_text", "input_button", 
            "branch", "switch_scenario", "log_message", "channel_action",
            "mongo_insert_document", "mongo_upsert_document", "mongo_find_documents",
            "mongo_find_one_document", "mongo_update_document", "mongo_delete_document",
            "llm_query", "llm_chat", "rag_search", "rag_answer",
            "amocrm_create_contact", "amocrm_find_contact", "amocrm_create_lead",
            "amocrm_find_lead", "amocrm_add_note", "amocrm_search",
            "http_get", "http_post", "http_put", "http_delete", "http_request",
            "scheduler_create_task", "scheduler_list_tasks", "scheduler_get_task", 
            "scheduler_cancel_task", "scheduler_get_stats",
            "pdf_generate", "conditional_execute"
        ]
    
    def _find_best_match(self, step_type: str) -> Tuple[str, float]:
        """Находит наиболее похожий поддерживаемый тип шага"""
        # Сначала проверяем прямое соответствие в маппинге
        if step_type in STEP_TYPE_MAPPING:
            mapped_type = STEP_TYPE_MAPPING[step_type]
            if mapped_type in self.supported_handlers:
                return mapped_type, 1.0
        
        # Поиск по схожести названий
        best_match = None
        best_ratio = 0.0
        
        for handler in self.supported_handlers:
            ratio = SequenceMatcher(None, step_type.lower(), handler.lower()).ratio()
            if ratio > best_ratio:
                best_ratio = ratio
                best_match = handler
        
        return best_match, best_ratio
    
    def _fix_step_params(self, step: Dict[str, Any], old_type: str, new_type: str) -> Dict[str, Any]:
        """Исправляет параметры шага при смене типа"""
        if not step.get("params"):
            step["params"] = {}
            
        params = step["params"]
        
        # Исправления для channel_action
        if new_type == "channel_action":
            if old_type in ["telegram_send_message", "send_message"]:
                params["action"] = "send_message"
                if "text" in params and "chat_id" not in params:
                    params["chat_id"] = "{chat_id}"
                    
            elif old_type in ["telegram_edit_message", "edit_message"]:
                params["action"] = "edit_message"
                if "chat_id" not in params:
                    params["chat_id"] = "{chat_id}"
                    
            elif old_type in ["telegram_send_buttons", "send_buttons"]:
                params["action"] = "send_message"
                if "chat_id" not in params:
                    params["chat_id"] = "{chat_id}"
                    
            elif old_type in ["copy_message"]:
                params["action"] = "copy_message" 
                if "chat_id" not in params:
                    params["chat_id"] = "{chat_id}"
        
        # Исправления для action
        elif new_type == "action":
            if old_type in ["set_context", "update_context"]:
                if "action" not in params:
                    params["action"] = "update_context"
        
        # Исправления для mongo операций
        elif new_type.startswith("mongo_"):
            if "collection" not in params:
                params["collection"] = "default_collection"  # Требует ручной настройки
        
        # Исправления для AmoCRM
        elif new_type.startswith("amocrm_"):
            # Базовые параметры уже должны быть правильными
            pass
            
        return step
    
    def validate_and_fix_scenario(self, scenario_data: Dict[str, Any]) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Валидирует и исправляет один сценарий.
        
        Args:
            scenario_data: Данные сценария
            
        Returns:
            Tuple[Dict, List]: (исправленный_сценарий, список_исправлений)
        """
        fixes = []
        fixed_scenario = copy.deepcopy(scenario_data)
        
        if "steps" not in fixed_scenario:
            return fixed_scenario, fixes
            
        for step in fixed_scenario["steps"]:
            step_id = step.get("id", "unknown")
            
            # Исправляем тип шага
            old_type = step.get("type")
            fixed_type = self._fix_step_type(step)
            if fixed_type != old_type:
                fixes.append({
                    "type": "step_type_fix",
                    "step_id": step_id,
                    "old_value": old_type,
                    "new_value": fixed_type
                })
            
            # Исправляем параметры action
            if step.get("type") == "action" and "params" in step:
                old_action = step["params"].get("action")
                self._fix_action_params(step)
                new_action = step["params"].get("action")
                
                if old_action and not new_action:
                    fixes.append({
                        "type": "action_fix", 
                        "step_id": step_id,
                        "old_value": old_action,
                        "new_value": "removed (data moved to params)"
                    })
            
            # Исправляем отсутствующие обязательные параметры
            missing_params = self._fix_missing_required_params(step)
            for param in missing_params:
                fixes.append({
                    "type": "missing_param_fix",
                    "step_id": step_id,
                    "param": param
                })
            
            # Исправляем структуру кнопок
            if self._fix_inline_keyboard_structure(step):
                fixes.append({
                    "type": "inline_keyboard_fix",
                    "step_id": step_id
                })
                
        return fixed_scenario, fixes
    
    def _validate_step_params(self, step: Dict[str, Any]) -> str:
        """Валидирует параметры конкретного шага"""
        step_type = step["type"]
        params = step.get("params", {})
        step_id = step.get("id", "unknown")
        
        # Проверки для channel_action
        if step_type == "channel_action":
            if "action" not in params:
                return f"⚠️ Шаг '{step_id}': отсутствует обязательный параметр 'action' для channel_action"
            
            action = params["action"]
            if action in ["send_message", "edit_message", "copy_message"] and "chat_id" not in params:
                # Автоисправление
                params["chat_id"] = "{chat_id}"
                return f"🔧 Шаг '{step_id}': добавлен отсутствующий chat_id"
        
        # Проверки для mongo операций
        elif step_type.startswith("mongo_"):
            if "collection" not in params:
                return f"⚠️ Шаг '{step_id}': отсутствует обязательный параметр 'collection'"
        
        return None
    
    def validate_file(self, file_path: str, fix_issues: bool = True) -> bool:
        """Валидирует файл сценария"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                scenario_data = yaml.safe_load(f)
                
            print(f"\n🔍 Валидация файла: {file_path}")
            
            fixed_scenario, fixes = self.validate_and_fix_scenario(scenario_data)
            
            if fixes:
                print("📋 Найденные проблемы:")
                for fix in fixes:
                    print(f"  {fix}")
                    
            if self.fixes_applied:
                print("🔧 Применённые исправления:")
                for fix in self.fixes_applied:
                    print(f"  ✅ {fix}")
                    
                if fix_issues:
                    # Сохраняем исправленный файл
                    with open(file_path, 'w', encoding='utf-8') as f:
                        yaml.dump(fixed_scenario, f, default_flow_style=False, 
                                allow_unicode=True, sort_keys=False)
                    print(f"💾 Файл {file_path} обновлён с исправлениями")
                    
                self.fixes_applied.clear()  # Очищаем для следующего файла
                
            if not fixes and not self.fixes_applied:
                print("✅ Файл валиден, исправления не требуются")
                
            return True
            
        except Exception as e:
            print(f"❌ Ошибка при валидации файла {file_path}: {e}")
            return False

    def _fix_action_params(self, step: Dict[str, Any]) -> bool:
        """Исправляет параметры action если они неправильные"""
        if step.get("type") != "action":
            return False
            
        params = step.get("params", {})
        action = params.get("action")
        
        if action in ACTION_MAPPING:
            fixed = False
            
            if action in ["update_context", "set_context", "store_context"]:
                # Убираем action, оставляем только data для обновления контекста
                if "data" in params:
                    # Перемещаем данные из data в корень params
                    data = params.pop("data")
                    params.pop("action")  # Убираем action
                    
                    # Добавляем данные в params для прямого обновления контекста
                    for key, value in data.items():
                        params[key] = value
                        
                    self.fixes_applied.append(f"Убрал action '{action}' и переместил data в params для прямого обновления контекста в шаге '{step.get('id', 'unknown')}'")
                    fixed = True
                else:
                    # Если нет data, просто убираем action
                    params.pop("action")
                    self.fixes_applied.append(f"Убрал неподдерживаемый action '{action}' в шаге '{step.get('id', 'unknown')}'")
                    fixed = True
                    
            return fixed
            
        return False

    def _find_similar_handler(self, invalid_type: str) -> str:
        """Находит наиболее похожий поддерживаемый handler"""
        if invalid_type in STEP_TYPE_MAPPING:
            return STEP_TYPE_MAPPING[invalid_type]
            
        # Ищем наиболее похожий по названию
        best_match = None
        best_ratio = 0.0
        
        for handler in self.supported_handlers:
            ratio = SequenceMatcher(None, invalid_type.lower(), handler.lower()).ratio()
            if ratio > best_ratio and ratio > 0.6:  # Минимальное сходство 60%
                best_ratio = ratio
                best_match = handler
                
        return best_match or "action"  # Fallback на action

    def _fix_step_type(self, step: Dict[str, Any]) -> str:
        """Исправляет тип шага если он неподдерживаемый и возвращает новый тип"""
        step_type = step.get("type")
        if not step_type:
            return step_type
            
        if step_type not in self.supported_handlers:
            new_type = self._find_similar_handler(step_type)
            step["type"] = new_type
            
            # Дополнительные исправления в зависимости от типа
            if step_type in ["telegram_send_message", "telegram_edit_message", "telegram_send_buttons"]:
                # Добавляем action для channel_action
                if "params" not in step:
                    step["params"] = {}
                if "action" not in step["params"]:
                    if step_type == "telegram_send_message":
                        step["params"]["action"] = "send_message"
                    elif step_type == "telegram_edit_message":
                        step["params"]["action"] = "edit_message"
                    elif step_type == "telegram_send_buttons":
                        step["params"]["action"] = "send_buttons"
                        
                # Добавляем chat_id если отсутствует
                if "chat_id" not in step["params"]:
                    step["params"]["chat_id"] = "{chat_id}"
                    
            elif step_type in ["wait_for_input", "get_input", "user_input"]:
                # Исправления для input
                if "params" not in step:
                    step["params"] = {}
                if "input_type" not in step["params"]:
                    step["params"]["input_type"] = "text"
                    
            elif step_type in ["store_data", "save_data"]:
                # Исправления для mongo операций
                if "params" not in step:
                    step["params"] = {}
                if "collection" not in step["params"]:
                    step["params"]["collection"] = "default_collection"
            
            return new_type
        
        return step_type

    def _fix_missing_required_params(self, step: Dict[str, Any]) -> List[str]:
        """Добавляет отсутствующие обязательные параметры и возвращает список добавленных параметров"""
        step_type = step.get("type")
        params = step.get("params", {})
        added_params = []
        
        if step_type == "channel_action":
            # Проверяем обязательные параметры для channel_action
            if "action" not in params:
                params["action"] = "send_message"
                added_params.append("action")
                
            if "chat_id" not in params:
                params["chat_id"] = "{chat_id}"
                added_params.append("chat_id")
                
        elif step_type in ["mongo_insert_document", "mongo_upsert_document", "mongo_update_document"]:
            if "collection" not in params:
                params["collection"] = "default_collection"
                added_params.append("collection")
                
        elif step_type == "input":
            if "input_type" not in params:
                params["input_type"] = "text"
                added_params.append("input_type")
                
        if added_params:
            step["params"] = params
            
        return added_params

    def _fix_inline_keyboard_structure(self, step: Dict[str, Any]) -> bool:
        """Исправляет структуру inline_keyboard (должна быть array of arrays)"""
        params = step.get("params", {})
        reply_markup = params.get("reply_markup", {})
        inline_keyboard = reply_markup.get("inline_keyboard")
        
        if inline_keyboard and isinstance(inline_keyboard, list):
            fixed = False
            
            # Проверяем, что каждый элемент - это массив
            for i, row in enumerate(inline_keyboard):
                if isinstance(row, dict):  # Если это объект кнопки, а не массив
                    inline_keyboard[i] = [row]  # Оборачиваем в массив
                    fixed = True
                    
            if fixed:
                self.fixes_applied.append(f"Исправил структуру inline_keyboard в шаге '{step.get('id', 'unknown')}'")
                return True
                
        return False

def main():
    parser = argparse.ArgumentParser(description="Валидатор сценариев с автоисправлением")
    parser.add_argument("files", nargs="+", help="Файлы сценариев для валидации")
    parser.add_argument("--no-fix", action="store_true", help="Только валидация, без исправлений")
    parser.add_argument("--api-url", default="http://localhost:8085", help="URL API для получения списка handlers")
    
    args = parser.parse_args()
    
    validator = ScenarioValidator(api_base_url=args.api_url)
    
    print(f"🎯 Поддерживаемые handlers: {len(validator.supported_handlers)}")
    print(f"📝 Handlers: {', '.join(validator.supported_handlers[:10])}{'...' if len(validator.supported_handlers) > 10 else ''}")
    
    all_valid = True
    
    for file_path in args.files:
        if not validator.validate_file(file_path, fix_issues=not args.no_fix):
            all_valid = False
            
    if all_valid:
        print("\n🎉 Все файлы прошли валидацию!")
        sys.exit(0)
    else:
        print("\n❌ Некоторые файлы содержат ошибки")
        sys.exit(1)

if __name__ == "__main__":
    main() 