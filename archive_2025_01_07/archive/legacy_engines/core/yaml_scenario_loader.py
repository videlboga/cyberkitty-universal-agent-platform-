"""
YAML Scenario Loader для Universal Agent Platform

Принципы:
- ПРОСТОТА ПРЕВЫШЕ ВСЕГО
- Минимум зависимостей и абстракций 
- Прямая совместимость с SimpleScenarioEngine
- Валидация и контроль качества
"""

import yaml
from typing import Dict, Any, List, Optional
from loguru import logger
from pathlib import Path


class YAMLScenarioLoader:
    """
    Простой загрузчик YAML сценариев.
    
    Принцип: ОДИН класс для ОДНОЙ задачи - загрузка и валидация YAML.
    """
    
    def __init__(self):
        """Инициализация без лишних зависимостей."""
        self.supported_step_types = {
            # Базовые типы
            'start', 'end', 'action', 'input', 'conditional_execute', 
            'switch_scenario', 'log_message', 'branch',
            
            # MongoDB
            'mongo_insert_document', 'mongo_upsert_document', 
            'mongo_find_documents', 'mongo_find_one_document',
            'mongo_update_document', 'mongo_delete_document',
            
            # ChannelManager (правильная архитектура!)
            'channel_action',
            
            # LLM & RAG
            'llm_query', 'llm_chat', 'rag_search', 'rag_answer',
            
            # HTTP
            'http_get', 'http_post', 'http_put', 'http_delete', 'http_request',
            
            # AmoCRM
            'amocrm_find_contact', 'amocrm_create_contact',
            'amocrm_find_lead', 'amocrm_create_lead', 'amocrm_add_note',
            'amocrm_search',
            
            # Scheduler
            'scheduler_create_task', 'scheduler_list_tasks',
            'scheduler_get_task', 'scheduler_cancel_task', 'scheduler_get_stats'
        }
        
        logger.info("🔧 YAMLScenarioLoader инициализирован")
    
    def load_from_string(self, yaml_content: str) -> Dict[str, Any]:
        """
        Загружает сценарий из YAML строки.
        
        Args:
            yaml_content: YAML содержимое как строка
            
        Returns:
            Dict со сценарием, готовым для SimpleScenarioEngine
            
        Raises:
            ValueError: При ошибке парсинга или валидации
        """
        try:
            # Загружаем YAML с безопасным парсером
            scenario = yaml.safe_load(yaml_content)
            
            if not scenario:
                raise ValueError("YAML файл пустой или некорректный")
            
            # Валидируем структуру
            self._validate_scenario(scenario)
            
            # Преобразуем в формат совместимый с движком
            converted = self._convert_to_engine_format(scenario)
            
            logger.info(f"✅ YAML сценарий загружен: {converted.get('scenario_id', 'unknown')}")
            return converted
            
        except yaml.YAMLError as e:
            error_msg = f"❌ Ошибка парсинга YAML: {e}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        except Exception as e:
            error_msg = f"❌ Ошибка загрузки YAML сценария: {e}"
            logger.error(error_msg)
            raise ValueError(error_msg)
    
    def load_from_file(self, file_path: str) -> Dict[str, Any]:
        """
        Загружает сценарий из YAML файла.
        
        Args:
            file_path: Путь к YAML файлу
            
        Returns:
            Dict со сценарием
        """
        try:
            path = Path(file_path)
            if not path.exists():
                raise FileNotFoundError(f"YAML файл не найден: {file_path}")
            
            with open(path, 'r', encoding='utf-8') as f:
                yaml_content = f.read()
            
            return self.load_from_string(yaml_content)
            
        except Exception as e:
            error_msg = f"❌ Ошибка чтения YAML файла {file_path}: {e}"
            logger.error(error_msg)
            raise ValueError(error_msg)
    
    def convert_json_to_yaml(self, json_scenario: Dict[str, Any]) -> str:
        """
        Конвертирует JSON сценарий в YAML формат.
        
        Args:
            json_scenario: Сценарий в JSON формате
            
        Returns:
            YAML строка
        """
        try:
            # Преобразуем в YAML-friendly формат
            yaml_scenario = self._convert_from_json_format(json_scenario)
            
            # Генерируем YAML с читаемым форматированием
            yaml_content = yaml.dump(
                yaml_scenario,
                default_flow_style=False,
                allow_unicode=True,
                indent=2,
                sort_keys=False
            )
            
            logger.info(f"✅ JSON сценарий конвертирован в YAML: {json_scenario.get('scenario_id', 'unknown')}")
            return yaml_content
            
        except Exception as e:
            error_msg = f"❌ Ошибка конвертации JSON в YAML: {e}"
            logger.error(error_msg)
            raise ValueError(error_msg)
    
    def _validate_scenario(self, scenario: Dict[str, Any]) -> None:
        """Валидирует структуру YAML сценария."""
        # Обязательные поля
        required_fields = ['scenario_id', 'steps']
        for field in required_fields:
            if field not in scenario:
                raise ValueError(f"Отсутствует обязательное поле: {field}")
        
        # Проверяем шаги
        steps = scenario['steps']
        if not isinstance(steps, list) or len(steps) == 0:
            raise ValueError("Поле 'steps' должно быть непустым списком")
        
        # Валидируем каждый шаг
        step_ids = set()
        for i, step in enumerate(steps):
            self._validate_step(step, i)
            
            # Проверяем уникальность ID
            step_id = step['id']
            if step_id in step_ids:
                raise ValueError(f"Дублированный ID шага: {step_id}")
            step_ids.add(step_id)
        
        logger.debug(f"✅ Валидация YAML сценария {scenario['scenario_id']} прошла успешно")
    
    def _validate_step(self, step: Dict[str, Any], index: int) -> None:
        """Валидирует отдельный шаг."""
        # Обязательные поля шага
        required_step_fields = ['id', 'type']
        for field in required_step_fields:
            if field not in step:
                raise ValueError(f"В шаге {index} отсутствует поле: {field}")
        
        # Проверяем тип шага
        step_type = step['type']
        if step_type not in self.supported_step_types:
            raise ValueError(f"Неподдерживаемый тип шага: {step_type}")
        
        # Проверяем наличие params если нужно
        if step_type not in ['start', 'end'] and 'params' not in step:
            # Некоторые шаги могут работать без params
            if step_type not in ['action', 'log_message']:
                logger.warning(f"⚠️ Шаг {step['id']} типа {step_type} без параметров")
    
    def _convert_to_engine_format(self, yaml_scenario: Dict[str, Any]) -> Dict[str, Any]:
        """
        Преобразует YAML сценарий в формат для SimpleScenarioEngine.
        
        Основные преобразования:
        - Сохраняет структуру совместимую с движком
        - Обрабатывает переменные ${var} -> {var} для обратной совместимости
        """
        converted = {
            'scenario_id': yaml_scenario['scenario_id'],
            'steps': []
        }
        
        # Копируем initial_context если есть
        if 'initial_context' in yaml_scenario:
            converted['initial_context'] = yaml_scenario['initial_context']
        
        # Обрабатываем шаги
        for step in yaml_scenario['steps']:
            converted_step = {
                'id': step['id'],
                'type': step['type']
            }
            
            # Копируем params если есть
            if 'params' in step:
                converted_step['params'] = self._process_template_variables(step['params'])
            
            # Копируем next_step если есть
            if 'next_step' in step:
                converted_step['next_step'] = step['next_step']
            
            converted['steps'].append(converted_step)
        
        return converted
    
    def _convert_from_json_format(self, json_scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Преобразует JSON формат в YAML-friendly формат."""
        yaml_scenario = {
            'scenario_id': json_scenario['scenario_id']
        }
        
        # Добавляем initial_context если есть
        if 'initial_context' in json_scenario:
            yaml_scenario['initial_context'] = json_scenario['initial_context']
        
        # Обрабатываем шаги
        yaml_scenario['steps'] = []
        for step in json_scenario['steps']:
            yaml_step = {
                'id': step['id'],
                'type': step['type']
            }
            
            if 'params' in step:
                yaml_step['params'] = self._process_template_variables_reverse(step['params'])
            
            if 'next_step' in step:
                yaml_step['next_step'] = step['next_step']
            
            yaml_scenario['steps'].append(yaml_step)
        
        return yaml_scenario
    
    def _process_template_variables(self, obj: Any) -> Any:
        """
        Обрабатывает переменные в объекте: ${var} -> {var}
        Для обратной совместимости с текущим движком.
        """
        if isinstance(obj, str):
            # Пока оставляем как есть, движок работает с {var}
            return obj
        elif isinstance(obj, dict):
            return {k: self._process_template_variables(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._process_template_variables(item) for item in obj]
        else:
            return obj
    
    def _process_template_variables_reverse(self, obj: Any) -> Any:
        """
        Обратное преобразование: {var} -> ${var} для YAML
        """
        if isinstance(obj, str):
            # Заменяем {var} на ${var} для YAML
            import re
            return re.sub(r'\{([^}]+)\}', r'${\1}', obj)
        elif isinstance(obj, dict):
            return {k: self._process_template_variables_reverse(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._process_template_variables_reverse(item) for item in obj]
        else:
            return obj


# Глобальный экземпляр для простоты использования
yaml_loader = YAMLScenarioLoader() 