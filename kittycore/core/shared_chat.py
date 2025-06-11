"""
💬 SharedChat - Система координации агентов

Обеспечивает координацию команды агентов через общий чат:
- Общий канал коммуникации для всех агентов
- История сообщений и контекста
- Координация действий и распределение задач
- Синхронизация результатов
"""

import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
from loguru import logger
from ..memory.collective_memory import CollectiveMemory


@dataclass
class ChatMessage:
    """Сообщение в общем чате"""
    id: str
    sender: str  # ID агента
    sender_role: str  # Роль агента
    content: str
    message_type: str  # 'info', 'question', 'result', 'coordination', 'request'
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    addressed_to: Optional[str] = None  # Кому адресовано (или None для всех)
    requires_response: bool = False


@dataclass 
class AgentPresence:
    """Присутствие агента в чате"""
    agent_id: str
    agent_role: str
    status: str  # 'active', 'busy', 'idle', 'offline'
    last_seen: datetime = field(default_factory=datetime.now)
    current_task: Optional[str] = None


class SharedChat:
    """Общий чат для координации агентов"""
    
    def __init__(self, team_id: str = "default", collective_memory: Optional[CollectiveMemory] = None):
        self.team_id = team_id
        self.messages: List[ChatMessage] = []
        self.agents: Dict[str, AgentPresence] = {}
        self.subscribers: Dict[str, Set[callable]] = {}  # Подписчики на события
        self.coordinator_id: Optional[str] = None
        self.collective_memory = collective_memory
        self._message_counter = 0
        
        logger.info(f"Создан SharedChat для команды: {team_id}")
    
    def register_agent(self, agent_id: str, agent_role: str, is_coordinator: bool = False) -> None:
        """Регистрация агента в чате"""
        self.agents[agent_id] = AgentPresence(
            agent_id=agent_id,
            agent_role=agent_role,
            status='active'
        )
        
        if is_coordinator:
            self.coordinator_id = agent_id
            logger.info(f"Агент {agent_id} ({agent_role}) назначен координатором")
        
        # Приветственное сообщение
        welcome_msg = ChatMessage(
            id=self._generate_message_id(),
            sender="system",
            sender_role="system",
            content=f"Агент {agent_role} ({agent_id}) присоединился к команде",
            message_type="info"
        )
        self.messages.append(welcome_msg)
        
        logger.info(f"Агент {agent_id} ({agent_role}) зарегистрирован в чате")
    
    def unregister_agent(self, agent_id: str) -> None:
        """Отключение агента от чата"""
        if agent_id in self.agents:
            agent_role = self.agents[agent_id].agent_role
            del self.agents[agent_id]
            
            # Сообщение об уходе
            goodbye_msg = ChatMessage(
                id=self._generate_message_id(),
                sender="system",
                sender_role="system", 
                content=f"Агент {agent_role} ({agent_id}) покинул команду",
                message_type="info"
            )
            self.messages.append(goodbye_msg)
            
            logger.info(f"Агент {agent_id} отключён от чата")
    
    async def send_message(self, sender_id: str, content: str, message_type: str = "info", 
                          addressed_to: Optional[str] = None, metadata: Dict[str, Any] = None,
                          requires_response: bool = False) -> str:
        """Отправить сообщение в чат"""
        
        if sender_id not in self.agents and sender_id != "system":
            raise ValueError(f"Агент {sender_id} не зарегистрирован в чате")
        
        message = ChatMessage(
            id=self._generate_message_id(),
            sender=sender_id,
            sender_role=self.agents.get(sender_id, AgentPresence("system", "system", "active")).agent_role,
            content=content,
            message_type=message_type,
            addressed_to=addressed_to,
            metadata=metadata or {},
            requires_response=requires_response
        )
        
        self.messages.append(message)
        
        # Обновляем статус отправителя
        if sender_id in self.agents:
            self.agents[sender_id].last_seen = datetime.now()
        
        # Уведомляем подписчиков
        await self._notify_subscribers('message', message)
        
        # Сохраняем в коллективную память
        if self.collective_memory:
            await self.collective_memory.add_memory(
                agent_id=sender_id,
                content=f"Сообщение в чат: {content}",
                memory_type="communication",
                metadata={
                    'chat_message_id': message.id,
                    'message_type': message_type,
                    'addressed_to': addressed_to
                }
            )
        
        logger.debug(f"Сообщение от {sender_id}: {content[:50]}...")
        return message.id
    
    async def broadcast_update(self, sender_id: str, update: str, task_info: Dict[str, Any] = None) -> None:
        """Рассылка обновления всем агентам"""
        await self.send_message(
            sender_id=sender_id,
            content=f"📢 Обновление: {update}",
            message_type="coordination",
            metadata={'task_info': task_info or {}}
        )
    
    async def request_help(self, sender_id: str, problem: str, expertise_needed: str = None) -> str:
        """Запрос помощи от команды"""
        content = f"🆘 Нужна помощь: {problem}"
        if expertise_needed:
            content += f"\nТребуется экспертиза: {expertise_needed}"
        
        return await self.send_message(
            sender_id=sender_id,
            content=content,
            message_type="request",
            requires_response=True,
            metadata={'problem': problem, 'expertise_needed': expertise_needed}
        )
    
    async def coordinate_task(self, coordinator_id: str, task: str, assignments: Dict[str, str]) -> List[str]:
        """Координация задачи - распределение между агентами"""
        message_ids = []
        
        # Общее объявление
        general_msg_id = await self.send_message(
            sender_id=coordinator_id,
            content=f"🎯 Новая задача: {task}",
            message_type="coordination"
        )
        message_ids.append(general_msg_id)
        
        # Индивидуальные назначения
        for agent_id, assignment in assignments.items():
            if agent_id in self.agents:
                msg_id = await self.send_message(
                    sender_id=coordinator_id,
                    content=f"📋 Ваше задание: {assignment}",
                    message_type="coordination",
                    addressed_to=agent_id,
                    metadata={'task': task, 'assignment': assignment}
                )
                message_ids.append(msg_id)
                
                # Обновляем текущую задачу агента
                self.agents[agent_id].current_task = assignment
        
        return message_ids
    
    async def report_result(self, sender_id: str, task: str, result: Dict[str, Any], 
                           success: bool = True) -> str:
        """Отчёт о результате выполнения"""
        
        status_emoji = "✅" if success else "❌"
        content = f"{status_emoji} Результат задачи: {task}"
        
        if success:
            content += f"\n📊 Успешно выполнено"
        else:
            error = result.get('error', 'Неизвестная ошибка')
            content += f"\n⚠️ Ошибка: {error}"
        
        # Добавляем краткую сводку результата
        if 'summary' in result:
            content += f"\n📝 Сводка: {result['summary']}"
        
        msg_id = await self.send_message(
            sender_id=sender_id,
            content=content,
            message_type="result",
            metadata={'task': task, 'result': result, 'success': success}
        )
        
        # Очищаем текущую задачу агента
        if sender_id in self.agents:
            self.agents[sender_id].current_task = None
        
        return msg_id
    
    def update_agent_status(self, agent_id: str, status: str, current_task: str = None) -> None:
        """Обновить статус агента"""
        if agent_id in self.agents:
            self.agents[agent_id].status = status
            self.agents[agent_id].last_seen = datetime.now()
            if current_task is not None:
                self.agents[agent_id].current_task = current_task
            
            logger.debug(f"Статус агента {agent_id}: {status}")
    
    def get_recent_messages(self, limit: int = 20, message_type: str = None,
                           since: datetime = None) -> List[ChatMessage]:
        """Получить недавние сообщения"""
        messages = self.messages
        
        if message_type:
            messages = [msg for msg in messages if msg.message_type == message_type]
        
        if since:
            messages = [msg for msg in messages if msg.timestamp > since]
        
        return messages[-limit:] if limit else messages
    
    def get_messages_for_agent(self, agent_id: str, limit: int = 10) -> List[ChatMessage]:
        """Получить сообщения адресованные конкретному агенту"""
        agent_messages = [
            msg for msg in self.messages
            if msg.addressed_to == agent_id or msg.addressed_to is None
        ]
        return agent_messages[-limit:] if limit else agent_messages
    
    def get_team_status(self) -> Dict[str, Any]:
        """Статус команды"""
        active_agents = [a for a in self.agents.values() if a.status == 'active']
        busy_agents = [a for a in self.agents.values() if a.status == 'busy']
        
        return {
            'team_id': self.team_id,
            'total_agents': len(self.agents),
            'active_agents': len(active_agents),
            'busy_agents': len(busy_agents),
            'coordinator': self.coordinator_id,
            'total_messages': len(self.messages),
            'agents': {
                agent_id: {
                    'role': agent.agent_role,
                    'status': agent.status,
                    'last_seen': agent.last_seen.isoformat(),
                    'current_task': agent.current_task
                }
                for agent_id, agent in self.agents.items()
            }
        }
    
    def get_conversation_summary(self, last_n_messages: int = 50) -> str:
        """Краткая сводка разговора для контекста"""
        recent_messages = self.get_recent_messages(last_n_messages)
        
        summary_parts = []
        summary_parts.append(f"Команда: {len(self.agents)} агентов")
        
        if recent_messages:
            summary_parts.append("Недавние сообщения:")
            for msg in recent_messages[-10:]:  # Последние 10
                sender_role = msg.sender_role
                content_preview = msg.content[:100] + "..." if len(msg.content) > 100 else msg.content
                summary_parts.append(f"- {sender_role}: {content_preview}")
        
        return "\n".join(summary_parts)
    
    async def subscribe_to_events(self, agent_id: str, callback: callable, event_types: List[str] = None) -> None:
        """Подписка на события чата"""
        if agent_id not in self.subscribers:
            self.subscribers[agent_id] = set()
        
        self.subscribers[agent_id].add(callback)
        logger.debug(f"Агент {agent_id} подписан на события чата")
    
    async def _notify_subscribers(self, event_type: str, data: Any) -> None:
        """Уведомление подписчиков"""
        for agent_id, callbacks in self.subscribers.items():
            for callback in callbacks:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(event_type, data)
                    else:
                        callback(event_type, data)
                except Exception as e:
                    logger.error(f"Ошибка уведомления подписчика {agent_id}: {e}")
    
    def _generate_message_id(self) -> str:
        """Генерация уникального ID сообщения"""
        self._message_counter += 1
        return f"{self.team_id}_msg_{self._message_counter}_{int(datetime.now().timestamp())}"
    
    def clear_history(self, keep_last: int = 100) -> None:
        """Очистка истории сообщений"""
        if len(self.messages) > keep_last:
            removed_count = len(self.messages) - keep_last
            self.messages = self.messages[-keep_last:]
            logger.info(f"Очищено {removed_count} старых сообщений из чата")
    
    def export_conversation(self) -> Dict[str, Any]:
        """Экспорт истории разговора"""
        return {
            'team_id': self.team_id,
            'agents': {
                agent_id: {
                    'role': agent.agent_role,
                    'status': agent.status,
                    'last_seen': agent.last_seen.isoformat()
                }
                for agent_id, agent in self.agents.items()
            },
            'messages': [
                {
                    'id': msg.id,
                    'sender': msg.sender,
                    'sender_role': msg.sender_role,
                    'content': msg.content,
                    'type': msg.message_type,
                    'timestamp': msg.timestamp.isoformat(),
                    'addressed_to': msg.addressed_to,
                    'metadata': msg.metadata
                }
                for msg in self.messages
            ],
            'total_messages': len(self.messages),
            'coordinator': self.coordinator_id
        } 