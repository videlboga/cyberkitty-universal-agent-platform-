import os
import json
import requests
from typing import Dict, Any, List, Optional
from loguru import logger
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from app.utils.dialog_state import DialogStateManager

# Настройка логирования
os.makedirs("logs", exist_ok=True)
logger.add("logs/agent_manager.log", format="{time} {level} {message}", level="INFO", rotation="10 MB", compression="zip", serialize=True)

class AgentManagerPlugin:
    """
    Плагин для управления агентами и переключения между ними.
    Добавляет поддержку специальных типов шагов:
    - agent_menu: отображает меню с доступными агентами
    - switch_agent: переключает активного агента
    - return_to_menu: возвращает в главное меню агентов
    """
    
    def __init__(self, api_base_url: str = "http://localhost:8000"):
        """
        Инициализация плагина
        
        Args:
            api_base_url: Базовый URL API для работы с коллекциями и агентами
        """
        self.api_base_url = api_base_url
        self.dialog_state_manager = DialogStateManager(api_base_url)
        logger.info("AgentManagerPlugin инициализирован")
    
    async def agent_menu(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Обработчик шага agent_menu
        Формирует меню для выбора агента
        
        Args:
            step_data: Данные шага (тип, текст меню, опции)
            context: Контекст сценария
            
        Returns:
            Dict: Обновленный контекст
        """
        try:
            user_id = context.get("user_id")
            chat_id = context.get("chat_id")
            
            if not user_id or not chat_id:
                logger.error("Ошибка: отсутствуют user_id или chat_id в контексте")
                return context
            
            # Получаем текст меню
            menu_text = step_data.get("text", "Выберите агента:")
            
            # Получаем список агентов для меню
            agents = step_data.get("agents", [
                {"id": "coach", "name": "Коуч", "description": "помогает с рефлексией по прогрессу"},
                {"id": "lifehacker", "name": "Лайфхакер", "description": "делится полезными советами"},
                {"id": "mentor", "name": "Ментор", "description": "отвечает на вопросы"},
                {"id": "digest", "name": "Дайджест", "description": "присылает новости"},
                {"id": "expert", "name": "Эксперт", "description": "помогает с решением задач"}
            ])
            
            # Создаем список кнопок для меню
            buttons = []
            for agent in agents:
                button_text = f"{agent['name']} - {agent['description']}" if "description" in agent else agent["name"]
                buttons.append([InlineKeyboardButton(button_text, callback_data=f"agent:{agent['id']}")])
            
            # Сохраняем список агентов в контексте
            context["available_agents"] = agents
            
            # Формируем меню в формате, понятном для Telegram
            context["agent_menu"] = {
                "text": menu_text,
                "reply_markup": {"inline_keyboard": [[button[0].text, button[0].callback_data] for button in buttons]}
            }
            
            # Обновляем состояние диалога
            await self.dialog_state_manager.update_step(user_id, "agent_menu")
            
            # Добавляем информацию о текущем активном агенте (none - в меню)
            await self.dialog_state_manager.set_current_agent(user_id, None)
            
            logger.info(f"Сформировано меню агентов для пользователя {user_id}")
            return context
            
        except Exception as e:
            logger.error(f"Ошибка при формировании меню агентов: {e}")
            return context
    
    async def switch_agent(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Обработчик шага switch_agent
        Переключает активного агента и запускает его сценарий
        
        Args:
            step_data: Данные шага (тип, agent_id, scenario_id)
            context: Контекст сценария
            
        Returns:
            Dict: Обновленный контекст
        """
        try:
            user_id = context.get("user_id")
            chat_id = context.get("chat_id")
            
            if not user_id or not chat_id:
                logger.error("Ошибка: отсутствуют user_id или chat_id в контексте")
                return context
            
            # Получаем ID агента
            agent_id = step_data.get("agent_id")
            if not agent_id and "selected_agent" in context:
                agent_id = context["selected_agent"]
            
            if not agent_id:
                logger.error("Ошибка: не указан agent_id для переключения")
                return context
            
            # Получаем информацию об агенте из API
            agent_response = requests.get(f"{self.api_base_url}/agents/{agent_id}")
            
            if agent_response.status_code != 200:
                logger.error(f"Ошибка получения информации об агенте: {agent_response.status_code}")
                context["agent_error"] = f"Агент с ID {agent_id} не найден"
                return context
            
            agent = agent_response.json()
            
            # Получаем ID сценария из агента
            scenario_id = agent.get("config", {}).get("scenario_id")
            
            if not scenario_id:
                logger.error(f"У агента {agent_id} отсутствует scenario_id")
                context["agent_error"] = "У агента нет связанного сценария"
                return context
            
            # Получаем сценарий из API
            scenario_response = requests.get(f"{self.api_base_url}/scenarios/{scenario_id}")
            
            if scenario_response.status_code != 200:
                logger.error(f"Ошибка получения сценария: {scenario_response.status_code}")
                context["agent_error"] = f"Сценарий с ID {scenario_id} не найден"
                return context
            
            # Сохраняем данные агента и сценария в контексте
            context["agent"] = agent
            context["agent_id"] = agent_id
            context["scenario_id"] = scenario_id
            context["agent_name"] = agent.get("name", agent_id)
            
            # Обновляем состояние диалога
            await self.dialog_state_manager.update_step(user_id, "agent_active")
            await self.dialog_state_manager.set_current_agent(user_id, agent_id)
            
            # Отправляем приветственное сообщение от агента
            welcome_message = step_data.get("welcome_message", f"Вы общаетесь с агентом: {context['agent_name']}. Чем могу помочь?")
            context["welcome_message"] = welcome_message
            
            logger.info(f"Пользователь {user_id} переключился на агента {agent_id}")
            return context
            
        except Exception as e:
            logger.error(f"Ошибка при переключении агента: {e}")
            return context
    
    async def return_to_menu(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Обработчик шага return_to_menu
        Возвращает пользователя в главное меню выбора агентов
        
        Args:
            step_data: Данные шага
            context: Контекст сценария
            
        Returns:
            Dict: Обновленный контекст
        """
        try:
            user_id = context.get("user_id")
            chat_id = context.get("chat_id")
            
            if not user_id or not chat_id:
                logger.error("Ошибка: отсутствуют user_id или chat_id в контексте")
                return context
            
            # Получаем текст для возврата в меню
            menu_text = step_data.get("text", "Вернулись в главное меню. Выберите агента:")
            
            # Создаем меню аналогично agent_menu
            agents = context.get("available_agents", [
                {"id": "coach", "name": "Коуч", "description": "помогает с рефлексией по прогрессу"},
                {"id": "lifehacker", "name": "Лайфхакер", "description": "делится полезными советами"},
                {"id": "mentor", "name": "Ментор", "description": "отвечает на вопросы"},
                {"id": "digest", "name": "Дайджест", "description": "присылает новости"},
                {"id": "expert", "name": "Эксперт", "description": "помогает с решением задач"}
            ])
            
            # Создаем список кнопок для меню
            buttons = []
            for agent in agents:
                button_text = f"{agent['name']} - {agent['description']}" if "description" in agent else agent["name"]
                buttons.append([InlineKeyboardButton(button_text, callback_data=f"agent:{agent['id']}")])
            
            # Формируем меню в формате, понятном для Telegram
            context["agent_menu"] = {
                "text": menu_text,
                "reply_markup": {"inline_keyboard": [[button[0].text, button[0].callback_data] for button in buttons]}
            }
            
            # Обновляем состояние диалога
            await self.dialog_state_manager.update_step(user_id, "agent_menu")
            await self.dialog_state_manager.set_current_agent(user_id, None)
            
            logger.info(f"Пользователь {user_id} вернулся в главное меню")
            return context
            
        except Exception as e:
            logger.error(f"Ошибка при возврате в меню: {e}")
            return context
    
    async def process_callback(self, callback_data: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Обрабатывает callback-запросы от inline-кнопок
        
        Args:
            callback_data: Данные callback-запроса
            context: Контекст сценария
            
        Returns:
            Dict: Обновленный контекст
        """
        try:
            if callback_data.startswith("agent:"):
                # Выбор агента из меню
                agent_id = callback_data.split(":", 1)[1]
                context["selected_agent"] = agent_id
                
                # Запускаем шаг switch_agent
                return await self.switch_agent({"agent_id": agent_id}, context)
            elif callback_data == "menu":
                # Возврат в главное меню
                return await self.return_to_menu({}, context)
            else:
                # Другие типы callback-запросов могут быть обработаны здесь
                logger.warning(f"Неизвестный callback: {callback_data}")
                return context
                
        except Exception as e:
            logger.error(f"Ошибка при обработке callback: {e}")
            return context
    
    def register_step_handlers(self, step_handlers: Dict[str, callable]):
        """
        Регистрирует обработчики специальных типов шагов
        
        Args:
            step_handlers: Словарь обработчиков шагов сценария
        """
        step_handlers["agent_menu"] = self.agent_menu
        step_handlers["switch_agent"] = self.switch_agent
        step_handlers["return_to_menu"] = self.return_to_menu
        logger.info("Зарегистрированы обработчики шагов для AgentManagerPlugin") 