"""
MetadataManager - упрощённое управление метаданными заметок Obsidian
"""

from datetime import datetime
from typing import Dict, List, Optional, Any


class MetadataManager:
    """
    Простой менеджер для создания метаданных заметок
    """
    
    def __init__(self):
        self.kittycore_version = "3.0"
    
    def create_agent_metadata(self, agent_name: str, agent_data: Dict[str, Any]) -> Dict[str, Any]:
        """Создание метаданных для заметки агента"""
        now = datetime.now().isoformat()
        
        return {
            "created": now,
            "modified": now,
            "type": "agent",
            "kittycore_version": self.kittycore_version,
            "agent_name": agent_name,
            "agent_type": agent_data.get('type', 'general'),
            "capabilities": agent_data.get('capabilities', []),
            "tasks_completed": agent_data.get('tasks_completed', 0),
            "success_rate": agent_data.get('success_rate', 0.0),
            "tags": ["agent", "kittycore", agent_name.lower()]
        }
    
    def create_task_metadata(self, task_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Создание метаданных для заметки задачи"""
        now = datetime.now().isoformat()
        
        return {
            "created": now,
            "modified": now,
            "type": "task",
            "kittycore_version": self.kittycore_version,
            "task_id": task_id,
            "status": task_data.get('status', 'pending'),
            "priority": task_data.get('priority', 'normal'),
            "assigned_agents": task_data.get('assigned_agents', []),
            "complexity": task_data.get('complexity', 'medium'),
            "tags": ["task", "kittycore", task_data.get('status', 'pending')]
        }
    
    def create_result_metadata(self, task_id: str, agent_name: str, result_data: Dict[str, Any]) -> Dict[str, Any]:
        """Создание метаданных для заметки результата"""
        now = datetime.now().isoformat()
        
        return {
            "created": now,
            "modified": now,
            "type": "result",
            "kittycore_version": self.kittycore_version,
            "task_id": task_id,
            "agent_name": agent_name,
            "success": result_data.get('success', False),
            "quality_score": result_data.get('quality_score', 0.0),
            "reviewed_by": result_data.get('reviewed_by', ''),
            "review_status": result_data.get('review_status', 'pending'),
            "tags": ["result", "kittycore", agent_name.lower()]
        }
    
    def create_report_metadata(self, task_id: str, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """Создание метаданных для итогового отчёта"""
        now = datetime.now().isoformat()
        
        return {
            "created": now,
            "modified": now,
            "type": "report",
            "kittycore_version": self.kittycore_version,
            "task_id": task_id,
            "overall_success": report_data.get('overall_success', False),
            "overall_quality": report_data.get('overall_quality', 0.0),
            "participating_agents": [agent.get('name', '') for agent in report_data.get('agents', [])],
            "tags": ["report", "kittycore", "completed"]
        }
    
    def update_metadata(self, existing_metadata: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Обновление существующих метаданных
        
        Args:
            existing_metadata: Существующие метаданные
            updates: Обновления
            
        Returns:
            Обновлённые метаданные
        """
        # Создание копии существующих метаданных
        updated_metadata = existing_metadata.copy()
        
        # Применение обновлений
        updated_metadata.update(updates)
        
        # Обновление времени модификации
        updated_metadata['modified'] = datetime.now().isoformat()
        
        # Обновление тегов если нужно
        if 'tags' in updates and 'tags' in existing_metadata:
            # Слияние тегов без дубликатов
            all_tags = list(set(existing_metadata['tags'] + updates['tags']))
            updated_metadata['tags'] = all_tags
        
        return updated_metadata
    
    def validate_metadata(self, metadata: Dict[str, Any], metadata_type: str) -> List[str]:
        """
        Валидация метаданных
        
        Args:
            metadata: Метаданные для проверки
            metadata_type: Тип метаданных (agent, task, result, report)
            
        Returns:
            Список ошибок валидации
        """
        errors = []
        
        # Базовая валидация
        required_fields = ['created', 'modified', 'type', 'tags']
        for field in required_fields:
            if field not in metadata:
                errors.append(f"Отсутствует обязательное поле: {field}")
        
        # Специфическая валидация по типу
        if metadata_type == 'agent':
            agent_required = ['agent_type', 'capabilities']
            for field in agent_required:
                if field not in metadata:
                    errors.append(f"Отсутствует поле агента: {field}")
        
        elif metadata_type == 'task':
            task_required = ['task_id', 'status']
            for field in task_required:
                if field not in metadata:
                    errors.append(f"Отсутствует поле задачи: {field}")
        
        elif metadata_type == 'result':
            result_required = ['task_id', 'agent_name', 'success']
            for field in result_required:
                if field not in metadata:
                    errors.append(f"Отсутствует поле результата: {field}")
        
        elif metadata_type == 'report':
            report_required = ['task_id', 'overall_success']
            for field in report_required:
                if field not in metadata:
                    errors.append(f"Отсутствует поле отчёта: {field}")
        
        # Валидация форматов
        if 'tags' in metadata and not isinstance(metadata['tags'], list):
            errors.append("Теги должны быть списком")
        
        if 'quality_score' in metadata:
            score = metadata['quality_score']
            if not isinstance(score, (int, float)) or score < 0 or score > 10:
                errors.append("Оценка качества должна быть числом от 0 до 10")
        
        return errors
    
    def extract_search_keywords(self, metadata: Dict[str, Any]) -> List[str]:
        """
        Извлечение ключевых слов для поиска
        
        Args:
            metadata: Метаданные
            
        Returns:
            Список ключевых слов
        """
        keywords = []
        
        # Добавление тегов
        if 'tags' in metadata:
            keywords.extend(metadata['tags'])
        
        # Добавление специфических полей
        searchable_fields = [
            'agent_type', 'status', 'priority',
            'agent_name', 'task_id', 'type'
        ]
        
        for field in searchable_fields:
            if field in metadata and metadata[field]:
                keywords.append(str(metadata[field]).lower())
        
        # Удаление дубликатов
        return list(set(keywords))
    
    def get_metadata_summary(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Создание краткой сводки метаданных
        
        Args:
            metadata: Полные метаданные
            
        Returns:
            Краткая сводка
        """
        summary = {
            'type': metadata.get('type', 'unknown'),
            'created': metadata.get('created', ''),
            'tags': metadata.get('tags', [])
        }
        
        # Добавление специфических полей
        metadata_type = metadata.get('type')
        
        if metadata_type == 'agent':
            summary['agent_type'] = metadata.get('agent_type', '')
            summary['success_rate'] = metadata.get('success_rate', 0)
        
        elif metadata_type == 'task':
            summary['status'] = metadata.get('status', '')
            summary['priority'] = metadata.get('priority', '')
        
        elif metadata_type == 'result':
            summary['success'] = metadata.get('success', False)
            summary['quality_score'] = metadata.get('quality_score', 0)
        
        elif metadata_type == 'report':
            summary['overall_success'] = metadata.get('overall_success', False)
            summary['overall_quality'] = metadata.get('overall_quality', 0)
        
        return summary 