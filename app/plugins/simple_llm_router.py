#!/usr/bin/env python3
"""
🧠 SIMPLE LLM ROUTER PLUGIN
Плагин умной маршрутизации задач для SimpleScenarioEngine

Интегрирует LLM-классификацию в основную архитектуру KittyCore
"""

import asyncio
import aiohttp
import time
import os
from typing import Dict, Any, Optional, List
from loguru import logger
from app.core.base_plugin import BasePlugin

class SimpleLLMRouterPlugin(BasePlugin):
    """
    🧠 Плагин умной маршрутизации с LLM
    
    HANDLERS:
    - llm_route_task: маршрутизация задачи к агенту
    - llm_get_routing_stats: статистика маршрутизации
    - llm_classify_request: классификация входящего запроса
    """
    
    def __init__(self):
        super().__init__()
        self.plugin_name = "simple_llm_router"
        
        # Доступные агенты в системе
        self.available_agents = {
            "nova": {
                "name": "📊 NovaAgent",
                "description": "Анализ данных, статистика, отчеты",
                "keywords": ["анализ", "данные", "статистика"],
                "scenario_id": "nova_analysis_scenario"
            },
            "sherlock": {
                "name": "🔍 SherlockAgent", 
                "description": "Поиск информации, исследования",
                "keywords": ["найди", "поиск", "исследуй"],
                "scenario_id": "sherlock_research_scenario"
            },
            "artemis": {
                "name": "🎨 ArtemisAgent",
                "description": "Контент, дизайн, тексты",
                "keywords": ["создай", "дизайн", "контент"],
                "scenario_id": "artemis_creative_scenario"
            },
            "ada": {
                "name": "💻 AdaAgent",
                "description": "Программирование, код",
                "keywords": ["код", "программа", "api"],
                "scenario_id": "ada_development_scenario"
            },
            "cipher": {
                "name": "🔒 CipherAgent",
                "description": "Безопасность, тестирование",
                "keywords": ["тест", "безопасность"],
                "scenario_id": "cipher_security_scenario"
            },
            "warren": {
                "name": "💰 WarrenAgent",
                "description": "Финансы, бюджет",
                "keywords": ["бюджет", "финансы"],
                "scenario_id": "warren_finance_scenario"
            },
            "viral": {
                "name": "📢 ViralAgent",
                "description": "Маркетинг, реклама",
                "keywords": ["реклама", "маркетинг"],
                "scenario_id": "viral_marketing_scenario"
            }
        }
        
        # Статистика
        self.stats = {
            "total_routes": 0,
            "llm_routes": 0,
            "heuristic_routes": 0,
            "successful_routes": 0,
            "agent_usage": {agent: 0 for agent in self.available_agents.keys()}
        }
        
        logger.info(f"🧠 {self.plugin_name}: готов с {len(self.available_agents)} агентами")
    
    def register_handlers(self) -> Dict[str, callable]:
        """Регистрация обработчиков"""
        return {
            "llm_route_task": self.llm_route_task,
            "llm_get_routing_stats": self.llm_get_routing_stats,
            "llm_classify_request": self.llm_classify_request,
            "llm_execute_with_agent": self.llm_execute_with_agent
        }
    
    async def llm_route_task(self, step: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Маршрутизация задачи к подходящему агенту
        
        Параметры step:
        - task: текст задачи для маршрутизации
        - priority: normal|high|critical
        - use_llm: true|false (принудительно)
        """
        
        try:
            task = step["params"]["task"]
            priority = step["params"].get("priority", "normal")
            force_llm = step["params"].get("use_llm", False)
            
            logger.info(f"🧠 Маршрутизация задачи: '{task[:50]}...' (приоритет: {priority})")
            
            # Определяем метод маршрутизации
            use_llm = force_llm or self._should_use_llm(task, priority)
            
            if use_llm:
                routing_result = await self._route_with_llm(task)
                self.stats["llm_routes"] += 1
                logger.info(f"🧠 LLM маршрутизация: {task[:30]}... → {routing_result['agent']}")
            else:
                routing_result = self._route_with_heuristics(task)
                self.stats["heuristic_routes"] += 1
                logger.info(f"🔧 Эвристическая маршрутизация: {task[:30]}... → {routing_result['agent']}")
            
            self.stats["total_routes"] += 1
            self.stats["successful_routes"] += 1
            self.stats["agent_usage"][routing_result["agent"]] += 1
            
            # Обновляем контекст результатом маршрутизации
            context.update({
                "selected_agent": routing_result["agent"],
                "agent_scenario": self.available_agents[routing_result["agent"]]["scenario_id"],
                "routing_confidence": routing_result["confidence"],
                "routing_method": routing_result["method"],
                "routing_reasoning": routing_result["reasoning"],
                "original_task": task
            })
            
            return {"success": True, "context": context, "routing": routing_result}
            
        except Exception as e:
            logger.error(f"❌ Ошибка маршрутизации: {e}")
            return {"success": False, "error": str(e), "context": context}
    
    async def llm_classify_request(self, step: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Классификация входящего запроса пользователя
        
        Параметры step:
        - user_message: сообщение пользователя
        - chat_id: ID чата (опционально)
        """
        
        try:
            user_message = step["params"]["user_message"]
            chat_id = step["params"].get("chat_id", "unknown")
            
            logger.info(f"🔍 Классификация запроса от {chat_id}: '{user_message[:50]}...'")
            
            # Определяем тип запроса
            request_type = await self._classify_request_type(user_message)
            
            # Если это задача для агента - маршрутизируем
            if request_type["is_task"]:
                routing_result = await self._route_with_llm(user_message)
                
                context.update({
                    "request_type": "agent_task",
                    "selected_agent": routing_result["agent"],
                    "agent_scenario": self.available_agents[routing_result["agent"]]["scenario_id"],
                    "classification": request_type,
                    "routing": routing_result,
                    "original_message": user_message
                })
            else:
                # Обычное сообщение - обрабатываем стандартно
                context.update({
                    "request_type": "regular_message",
                    "classification": request_type,
                    "original_message": user_message
                })
            
            return {"success": True, "context": context}
            
        except Exception as e:
            logger.error(f"❌ Ошибка классификации запроса: {e}")
            return {"success": False, "error": str(e), "context": context}
    
    async def llm_execute_with_agent(self, step: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Выполнение задачи выбранным агентом через переключение сценария
        """
        
        try:
            agent = context.get("selected_agent")
            agent_scenario = context.get("agent_scenario")
            original_task = context.get("original_task")
            
            if not agent or not agent_scenario:
                return {"success": False, "error": "Агент не выбран", "context": context}
            
            logger.info(f"🤖 Выполнение задачи агентом {agent}: {agent_scenario}")
            
            # Подготавливаем контекст для агента
            agent_context = {
                **context,
                "task": original_task,
                "agent_type": agent,
                "execution_start_time": time.time()
            }
            
            # Переключаемся на сценарий агента
            context.update({
                "switch_to_scenario": agent_scenario,
                "agent_context": agent_context,
                "execution_status": "started"
            })
            
            return {"success": True, "context": context}
            
        except Exception as e:
            logger.error(f"❌ Ошибка выполнения агентом: {e}")
            return {"success": False, "error": str(e), "context": context}
    
    async def llm_get_routing_stats(self, step: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Получение статистики маршрутизации"""
        
        total = self.stats["total_routes"]
        
        if total == 0:
            stats = {"message": "Нет данных о маршрутизации"}
        else:
            stats = {
                "total_routes": total,
                "llm_usage_percent": round((self.stats["llm_routes"] / total) * 100, 1),
                "heuristic_usage_percent": round((self.stats["heuristic_routes"] / total) * 100, 1),
                "success_rate": round((self.stats["successful_routes"] / total) * 100, 1),
                "agent_usage": self.stats["agent_usage"],
                "most_used_agent": max(self.stats["agent_usage"], key=self.stats["agent_usage"].get)
            }
        
        context["routing_stats"] = stats
        return {"success": True, "context": context}
    
    def _should_use_llm(self, task: str, priority: str) -> bool:
        """Определение необходимости использования LLM"""
        
        # Критичные задачи всегда через LLM
        if priority == "critical":
            return True
        
        # Проверяем на очевидные паттерны
        task_lower = task.lower()
        
        for agent_id, agent_info in self.available_agents.items():
            keywords = agent_info["keywords"]
            if any(keyword in task_lower for keyword in keywords):
                return False  # Очевидная задача - эвристика
        
        # Неоднозначная задача - LLM
        return True
    
    async def _route_with_llm(self, task: str) -> Dict[str, Any]:
        """Маршрутизация через LLM"""
        
        start_time = time.time()
        
        # Получаем настройки API
        settings = await self._get_fresh_settings()
        api_key = settings.get("openrouter_api_key") or os.getenv('OPENROUTER_API_KEY')
        
        if not api_key:
            raise Exception("API ключ не найден")
        
        # Создаем промпт
        agents_list = "\n".join([
            f"{agent_id} - {info['description']}" 
            for agent_id, info in self.available_agents.items()
        ])
        
        prompt = f"""Ты эксперт по классификации задач. Выбери ОДНОГО агента:

{agents_list}

ЗАДАЧА: {task}

ОТВЕТ: только имя агента (например: nova)"""
        
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "deepseek/deepseek-chat",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 15,
                "temperature": 0.1
            }
            
            async with session.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers, json=payload, timeout=12
            ) as response:
                
                response_time = round((time.time() - start_time) * 1000)
                
                if response.status == 200:
                    data = await response.json()
                    content = data["choices"][0]["message"]["content"]
                    agent = self._extract_agent_name(content)
                    
                    return {
                        "agent": agent,
                        "confidence": 0.91,
                        "method": "llm",
                        "reasoning": f"LLM: '{content.strip()}'",
                        "response_time_ms": response_time
                    }
                else:
                    raise Exception(f"HTTP {response.status}")
    
    def _route_with_heuristics(self, task: str) -> Dict[str, Any]:
        """Эвристическая маршрутизация"""
        
        task_lower = task.lower()
        
        # Проверяем по ключевым словам агентов
        for agent_id, agent_info in self.available_agents.items():
            keywords = agent_info["keywords"]
            if any(keyword in task_lower for keyword in keywords):
                return {
                    "agent": agent_id,
                    "confidence": 0.78,
                    "method": "heuristic",
                    "reasoning": f"Эвристика: совпадение ключевых слов",
                    "response_time_ms": 1
                }
        
        # По умолчанию - sherlock
        return {
            "agent": "sherlock",
            "confidence": 0.6,
            "method": "heuristic",
            "reasoning": "По умолчанию - универсальный агент",
            "response_time_ms": 1
        }
    
    async def _classify_request_type(self, message: str) -> Dict[str, Any]:
        """Классификация типа запроса"""
        
        message_lower = message.lower()
        
        # Определяем является ли это задачей для агента
        task_indicators = [
            "создай", "найди", "проанализируй", "разработай", "напиши",
            "рассчитай", "запусти", "исследуй", "протестируй", "изучи"
        ]
        
        is_task = any(indicator in message_lower for indicator in task_indicators)
        
        return {
            "is_task": is_task,
            "confidence": 0.8 if is_task else 0.9,
            "indicators_found": [ind for ind in task_indicators if ind in message_lower]
        }
    
    def _extract_agent_name(self, response: str) -> str:
        """Извлечение имени агента из ответа"""
        
        response_lower = response.lower()
        
        for agent_id in self.available_agents.keys():
            if agent_id in response_lower:
                return agent_id
        
        return "sherlock"  # По умолчанию
    
    async def _get_fresh_settings(self) -> Dict[str, Any]:
        """Загрузка свежих настроек (базовая реализация)"""
        return {
            "openrouter_api_key": os.getenv('OPENROUTER_API_KEY')
        } 