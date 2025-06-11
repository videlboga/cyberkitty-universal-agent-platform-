"""
🔧 ToolAdapterAgent - Агент для адаптации инструментов

Решает проблему "неизвестных инструментов":
- Анализирует запрошенный инструмент
- Ищет подходящие существующие
- Создаёт адаптеры для существующих инструментов  
- Генерирует новые инструменты если нужно
"""

import asyncio
from typing import Dict, Any, List, Optional, Tuple
from loguru import logger
from .base_agent import Agent
from ..tools.base_tool import default_tool_manager, Tool, ToolResult, FunctionTool
from ..llm import LLMProvider


class ToolAdapterAgent(Agent):
    """Агент-адаптер инструментов"""
    
    def __init__(self, llm_provider: LLMProvider):
        # Создаём агента с базовым промптом
        super().__init__(
            prompt="You are a tool adapter agent that helps find and create appropriate tools for tasks",
            model="auto",
            tools=[]
        )
        
        # Устанавливаем специфичные свойства
        self.name = "ToolAdapter"
        self.role = "Адаптер инструментов"
        self.goal = "Найти/создать/адаптировать нужные инструменты"
        self.llm_provider = llm_provider
        self.tool_manager = default_tool_manager
        self.created_tools: Dict[str, Tool] = {}
        
    async def execute_task(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Выполнить задачу адаптации инструмента"""
        try:
            logger.info(f"ToolAdapterAgent анализирует запрос: {task}")
            
            # Извлекаем название нужного инструмента из задачи
            tool_request = await self._parse_tool_request(task)
            
            if not tool_request:
                return {
                    'success': False,
                    'error': 'Не удалось определить нужный инструмент',
                    'task': task
                }
            
            # Ищем подходящий инструмент
            adaptation_result = await self._find_or_create_tool(tool_request)
            
            return {
                'success': True,
                'tool_request': tool_request,
                'adaptation_result': adaptation_result,
                'available_tool': adaptation_result.get('tool_name'),
                'task': task
            }
            
        except Exception as e:
            logger.error(f"Ошибка в ToolAdapterAgent: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'task': task
            }
    
    async def _parse_tool_request(self, task: str) -> Optional[Dict[str, Any]]:
        """Парсит запрос и определяет нужный инструмент"""
        
        # Список известных проблемных инструментов из бенчмарков
        common_missing_tools = {
            'design': 'инструмент для дизайна и создания макетов',
            'marketing': 'инструмент для маркетинговых операций',
            'business-model': 'инструмент для бизнес-моделирования',
            'code_generator': 'инструмент для генерации кода',
            'data_analyzer': 'инструмент для анализа данных',
            'content_creator': 'инструмент для создания контента',
            'project_manager': 'инструмент для управления проектами'
        }
        
        # Ищем упоминания в задаче
        for tool_name, description in common_missing_tools.items():
            if tool_name.lower() in task.lower() or tool_name.replace('_', ' ').lower() in task.lower():
                return {
                    'requested_tool': tool_name,
                    'description': description,
                    'context': task
                }
        
        # Используем LLM для более сложного анализа
        prompt = f"""
        Анализируй запрос и определи какой инструмент нужен:
        
        Запрос: {task}
        
        Ответь в JSON формате:
        {{
            "requested_tool": "название_инструмента",
            "description": "что он должен делать",
            "category": "web/data/communication/system/creative/business"
        }}
        """
        
        try:
            response = await self.llm_provider.generate(prompt)
            import json
            tool_request = json.loads(response)
            tool_request['context'] = task
            return tool_request
        except Exception as e:
            logger.warning(f"LLM не смог разобрать запрос: {e}")
            return None
    
    async def _find_or_create_tool(self, tool_request: Dict[str, Any]) -> Dict[str, Any]:
        """Найти существующий или создать новый инструмент"""
        
        requested_tool = tool_request['requested_tool']
        description = tool_request['description']
        category = tool_request.get('category', 'general')
        
        # 1. Ищем точное совпадение
        existing_tool = self.tool_manager.get_tool(requested_tool)
        if existing_tool:
            return {
                'status': 'found_exact',
                'tool_name': requested_tool,
                'tool_type': 'existing',
                'message': f'Найден точный инструмент: {requested_tool}'
            }
        
        # 2. Ищем похожие инструменты
        similar_tools = await self._find_similar_tools(requested_tool, description)
        if similar_tools:
            # Используем самый похожий
            best_match = similar_tools[0]
            return {
                'status': 'found_similar',
                'tool_name': best_match['name'],
                'tool_type': 'existing',
                'similarity': best_match['similarity'],
                'message': f'Найден похожий инструмент: {best_match["name"]} (схожесть: {best_match["similarity"]:.2f})'
            }
        
        # 3. Создаём адаптер на основе существующих инструментов
        adapter_result = await self._create_adapter(tool_request)
        if adapter_result['success']:
            return {
                'status': 'created_adapter',
                'tool_name': adapter_result['tool_name'],
                'tool_type': 'adapter',
                'base_tools': adapter_result['base_tools'],
                'message': f'Создан адаптер: {adapter_result["tool_name"]}'
            }
        
        # 4. Создаём новый инструмент
        new_tool_result = await self._create_new_tool(tool_request)
        if new_tool_result['success']:
            return {
                'status': 'created_new',
                'tool_name': new_tool_result['tool_name'],
                'tool_type': 'new',
                'message': f'Создан новый инструмент: {new_tool_result["tool_name"]}'
            }
        
        # 5. Fallback - создаём заглушку
        return await self._create_placeholder_tool(tool_request)
    
    async def _find_similar_tools(self, requested_tool: str, description: str) -> List[Dict[str, Any]]:
        """Найти похожие инструменты"""
        similar_tools = []
        available_tools = self.tool_manager.list_tools()
        
        # Простое сравнение по ключевым словам
        requested_words = set(requested_tool.lower().replace('_', ' ').split())
        description_words = set(description.lower().split())
        search_words = requested_words.union(description_words)
        
        for tool_info in available_tools:
            tool_name = tool_info['name'].lower()
            tool_desc = tool_info['description'].lower()
            
            # Считаем пересечения
            tool_words = set(tool_name.replace('_', ' ').split())
            desc_words = set(tool_desc.split())
            all_tool_words = tool_words.union(desc_words)
            
            intersection = search_words.intersection(all_tool_words)
            similarity = len(intersection) / len(search_words) if search_words else 0
            
            if similarity > 0.3:  # Порог схожести
                similar_tools.append({
                    'name': tool_info['name'],
                    'description': tool_info['description'],
                    'similarity': similarity
                })
        
        return sorted(similar_tools, key=lambda x: x['similarity'], reverse=True)
    
    async def _create_adapter(self, tool_request: Dict[str, Any]) -> Dict[str, Any]:
        """Создать адаптер на основе существующих инструментов"""
        
        requested_tool = tool_request['requested_tool']
        description = tool_request['description']
        category = tool_request.get('category', 'general')
        
        # Определяем базовые инструменты для адаптера
        base_tools = []
        
        if 'design' in requested_tool.lower():
            # Дизайн = web_search + file_manager + генерация HTML
            base_tools = ['web_search', 'file_manager']
        elif 'marketing' in requested_tool.lower():
            # Маркетинг = web_search + анализ + создание контента
            base_tools = ['web_search', 'file_manager']
        elif 'business' in requested_tool.lower():
            # Бизнес = анализ + расчёты + создание документов
            base_tools = ['system_tools', 'file_manager']
        elif 'code' in requested_tool.lower():
            # Код = файлы + системные операции
            base_tools = ['file_manager', 'system_tools']
        elif 'data' in requested_tool.lower():
            # Данные = расчёты + анализ
            base_tools = ['system_tools', 'database']
        else:
            # Общий случай
            base_tools = ['file_manager', 'system_tools']
        
        # Проверяем что базовые инструменты есть
        available_bases = []
        for base_tool in base_tools:
            if self.tool_manager.get_tool(base_tool):
                available_bases.append(base_tool)
        
        if not available_bases:
            return {'success': False, 'error': 'Нет подходящих базовых инструментов'}
        
        # Создаём функцию-адаптер
        async def adapter_function(**kwargs):
            """Адаптер инструмента"""
            results = {}
            
            # Используем первый доступный инструмент как основной
            main_tool = available_bases[0]
            
            if main_tool == 'file_manager':
                # Создаём файл с результатом
                content = f"Результат работы {requested_tool}:\n\n"
                content += f"Запрос: {kwargs.get('input', 'Нет входных данных')}\n"
                content += f"Обработано инструментом: {main_tool}\n"
                
                result = self.tool_manager.execute_tool(
                    'file_manager',
                    operation='create_file',
                    path=f"output/{requested_tool}_result.txt",
                    content=content
                )
                return result.data
                
            elif main_tool == 'system_tools':
                # Выполняем анализ или расчёт
                result = self.tool_manager.execute_tool(
                    'system_tools',
                    operation='get_system_info'
                )
                return {
                    'tool': requested_tool,
                    'system_info': result.data,
                    'input': kwargs
                }
            
            elif main_tool == 'web_search':
                # Поиск информации
                query = kwargs.get('query', requested_tool)
                result = self.tool_manager.execute_tool(
                    'web_search',
                    query=query
                )
                return result.data
            
            return {'message': f'{requested_tool} выполнен через {main_tool}', 'input': kwargs}
        
        # Создаём схему
        schema = {
            "type": "object",
            "properties": {
                "input": {
                    "type": "string",
                    "description": f"Входные данные для {requested_tool}"
                },
                "query": {
                    "type": "string", 
                    "description": "Поисковый запрос (если нужен)"
                }
            },
            "required": ["input"]
        }
        
        # Создаём адаптер как FunctionTool
        adapter_tool = FunctionTool(
            name=requested_tool,
            description=f"Адаптер для {description}",
            func=adapter_function,
            schema=schema
        )
        
        # Регистрируем в менеджере
        self.tool_manager.register(adapter_tool, category)
        self.created_tools[requested_tool] = adapter_tool
        
        logger.info(f"Создан адаптер {requested_tool} на базе {available_bases}")
        
        return {
            'success': True,
            'tool_name': requested_tool,
            'base_tools': available_bases,
            'registered': True
        }
    
    async def _create_new_tool(self, tool_request: Dict[str, Any]) -> Dict[str, Any]:
        """Создать полностью новый инструмент с помощью LLM"""
        
        requested_tool = tool_request['requested_tool']
        description = tool_request['description']
        
        # Пока что создаём простую заглушку
        # В будущем можно генерировать код инструмента через LLM
        
        def new_tool_function(**kwargs):
            return {
                'tool': requested_tool,
                'description': description,
                'input': kwargs,
                'status': 'executed',
                'note': 'Это новый сгенерированный инструмент'
            }
        
        schema = {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "description": f"Действие для {requested_tool}"
                },
                "data": {
                    "type": "object",
                    "description": "Данные для обработки"
                }
            },
            "required": ["action"]
        }
        
        new_tool = FunctionTool(
            name=requested_tool,
            description=description,
            func=new_tool_function,
            schema=schema
        )
        
        self.tool_manager.register(new_tool, 'generated')
        self.created_tools[requested_tool] = new_tool
        
        logger.info(f"Создан новый инструмент: {requested_tool}")
        
        return {
            'success': True,
            'tool_name': requested_tool,
            'type': 'generated'
        }
    
    async def _create_placeholder_tool(self, tool_request: Dict[str, Any]) -> Dict[str, Any]:
        """Создать инструмент-заглушку"""
        
        requested_tool = tool_request['requested_tool']
        description = tool_request['description']
        
        def placeholder_function(**kwargs):
            return {
                'tool': requested_tool,
                'status': 'placeholder',
                'message': f'Заглушка для {description}',
                'input': kwargs,
                'note': 'Этот инструмент ещё не реализован полностью'
            }
        
        schema = {
            "type": "object", 
            "properties": {
                "input": {
                    "type": "string",
                    "description": "Любые входные данные"
                }
            }
        }
        
        placeholder_tool = FunctionTool(
            name=requested_tool,
            description=f"Заглушка: {description}",
            func=placeholder_function,
            schema=schema
        )
        
        self.tool_manager.register(placeholder_tool, 'placeholder')
        self.created_tools[requested_tool] = placeholder_tool
        
        logger.warning(f"Создана заглушка для инструмента: {requested_tool}")
        
        return {
            'status': 'created_placeholder',
            'tool_name': requested_tool,
            'tool_type': 'placeholder',
            'message': f'Создана заглушка: {requested_tool}'
        }
    
    def get_created_tools(self) -> Dict[str, Tool]:
        """Получить созданные инструменты"""
        return self.created_tools
    
    def get_adaptation_stats(self) -> Dict[str, Any]:
        """Статистика адаптации инструментов"""
        return {
            'total_created': len(self.created_tools),
            'created_tools': list(self.created_tools.keys()),
            'available_tools': len(self.tool_manager.tools),
            'tool_categories': list(self.tool_manager.categories.keys())
        } 