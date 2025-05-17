import os
import json
import requests
from typing import Dict, Any, List
from loguru import logger
from datetime import datetime
from app.plugins.rag_plugin import RAGPlugin

# Настройка логирования
os.makedirs("logs", exist_ok=True)
logger.add("logs/learning_plan_plugin.log", format="{time} {level} {message}", level="INFO", rotation="10 MB", compression="zip", serialize=True)

class LearningPlanPlugin:
    """
    Плагин для обработки сценариев создания индивидуальных планов обучения.
    Добавляет поддержку специальных типов шагов:
    - process_user_profile: преобразует ответы пользователя в профиль
    - process_learning_plan: обрабатывает текстовый план в структурированный формат
    """
    
    def __init__(self, api_base_url: str = "http://localhost:8000"):
        """
        Инициализация плагина
        
        Args:
            api_base_url: Базовый URL API для работы с коллекциями
        """
        self.api_base_url = api_base_url
        self.rag_plugin = RAGPlugin()
        logger.info("LearningPlanPlugin инициализирован")
    
    async def process_user_profile(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Обработчик шага process_user_profile
        Преобразует ответы пользователя в структурированный профиль
        
        Args:
            step_data: Данные шага (тип, входные/выходные переменные)
            context: Контекст сценария
            
        Returns:
            Dict: Обновленный контекст с профилем пользователя
        """
        try:
            # Получаем входные переменные из контекста
            input_vars = step_data.get("input_vars", [])
            experience = context.get("experience", "beginner")
            interests = context.get("interests", [])
            learning_goals = context.get("learning_goals", [])
            learning_style = context.get("learning_style", "mixed")
            available_time = context.get("available_time", "5_to_10")
            notifications = context.get("notifications", "on_demand")
            
            # Преобразуем ответы в профиль
            profile = {
                "user_id": context.get("user_id"),
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            # Информация из Telegram, если есть
            if "first_name" in context:
                profile["first_name"] = context["first_name"]
            if "last_name" in context:
                profile["last_name"] = context["last_name"]
            if "username" in context:
                profile["username"] = context["username"]
            
            # Опыт
            experience_map = {
                "beginner": "начинающий",
                "intermediate": "средний",
                "advanced": "продвинутый"
            }
            profile["experience_level"] = experience_map.get(experience, "начинающий")
            
            # Интересы
            interests_map = {
                "computer_vision": "Компьютерное зрение",
                "nlp": "Обработка естественного языка",
                "generative_models": "Генеративные модели",
                "recommender_systems": "Рекомендательные системы",
                "business_automation": "Автоматизация бизнес-процессов",
                "healthcare": "Медицина и здравоохранение",
                "finance": "Финансы и трейдинг"
            }
            profile["interests"] = [interests_map.get(interest, interest) for interest in interests] if isinstance(interests, list) else []
            
            # Цели обучения
            goals_map = {
                "understand_basics": "Понимание основных принципов",
                "use_existing_solutions": "Использование готовых решений",
                "create_own_models": "Создание собственных моделей", 
                "apply_professionally": "Применение в профессиональной области",
                "career_change": "Начало карьеры в нейросетях"
            }
            profile["learning_goals"] = [goals_map.get(goal, goal) for goal in learning_goals] if isinstance(learning_goals, list) else []
            
            # Стиль обучения
            style_map = {
                "theoretical": "теоретический",
                "practical": "практический", 
                "mixed": "смешанный"
            }
            profile["preferred_learning_style"] = style_map.get(learning_style, "смешанный")
            
            # Доступное время
            time_map = {
                "less_than_5": "менее 5 часов",
                "5_to_10": "5-10 часов",
                "10_to_20": "10-20 часов",
                "more_than_20": "более 20 часов"
            }
            profile["available_time_per_week"] = time_map.get(available_time, "5-10 часов")
            
            # Уведомления
            profile["notifications_enabled"] = notifications != "none"
            if notifications == "daily":
                profile["notification_frequency"] = "daily"
                profile["daily_notification_time"] = "09:00"
            elif notifications == "weekly":
                profile["notification_frequency"] = "weekly"
                profile["weekly_notification_day"] = "monday"
                profile["weekly_notification_time"] = "10:00"
            else:
                profile["notification_frequency"] = "on_demand"
            
            # Добавляем профиль в контекст
            output_var = step_data.get("output_var", "user_profile")
            context[output_var] = profile
            
            logger.info(f"Профиль пользователя успешно обработан: user_id={profile.get('user_id')}")
            return context
            
        except Exception as e:
            logger.error(f"Ошибка при обработке профиля пользователя: {e}")
            # Добавляем заглушку в контекст
            output_var = step_data.get("output_var", "user_profile") 
            context[output_var] = {"user_id": context.get("user_id"), "error": str(e)}
            return context
    
    async def process_learning_plan(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Обработчик шага process_learning_plan
        Преобразует текстовый план обучения в структурированный формат
        
        Args:
            step_data: Данные шага (тип, входные/выходные переменные)
            context: Контекст сценария
            
        Returns:
            Dict: Обновленный контекст с планом обучения
        """
        try:
            # Получаем входные переменные из контекста
            input_vars = step_data.get("input_vars", [])
            plan_text = context.get("plan_text", "")
            user_profile = context.get("user_profile", {})
            
            # Создаем базовую структуру плана
            plan = {
                "user_id": user_profile.get("user_id"),
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "title": "Индивидуальный план обучения по нейросетям",
                "description": "План создан на основе ваших интересов и целей обучения",
                "raw_text": plan_text,
                "status": "active",
                "interests": user_profile.get("interests", []),
                "learning_goals": user_profile.get("learning_goals", []),
                "experience_level": user_profile.get("experience_level", "начинающий"),
                "preferred_learning_style": user_profile.get("preferred_learning_style", "смешанный"),
                "available_time_per_week": user_profile.get("available_time_per_week", "5-10 часов")
            }
            
            # Извлекаем структуру модулей из текста
            plan["modules"] = self._extract_modules_from_text(plan_text)
            
            # Создаем список модулей для отображения
            module_list = ""
            for i, module in enumerate(plan["modules"]):
                module_list += f"{i+1}. {module['title']}\n"
                if "description" in module:
                    module_list += f"   {module['description']}\n"
                if "estimated_time" in module:
                    module_list += f"   Время: {module['estimated_time']}\n"
                module_list += "\n"
            
            # Добавляем список модулей в контекст
            context["module_list"] = module_list
            
            # Добавляем план в контекст
            output_var = step_data.get("output_var", "learning_plan")
            context[output_var] = plan
            
            logger.info(f"План обучения успешно обработан: user_id={plan.get('user_id')}, модулей: {len(plan['modules'])}")
            return context
            
        except Exception as e:
            logger.error(f"Ошибка при обработке плана обучения: {e}")
            # Добавляем заглушку в контекст
            output_var = step_data.get("output_var", "learning_plan")
            context[output_var] = {
                "user_id": context.get("user_id"),
                "title": "Индивидуальный план обучения по нейросетям",
                "error": str(e),
                "modules": [
                    {
                        "title": "Введение в нейросети",
                        "description": "Базовые концепции и принципы работы",
                        "topics": ["Основы ИИ", "Типы нейросетей", "Области применения"],
                        "estimated_time": "1-2 недели"
                    }
                ]
            }
            context["module_list"] = "1. Введение в нейросети\n   Базовые концепции и принципы работы\n   Время: 1-2 недели\n\n"
            return context
    
    def _extract_modules_from_text(self, text: str) -> List[Dict[str, Any]]:
        """
        Извлекает структуру модулей из текстового плана
        
        Args:
            text: Текст плана обучения
            
        Returns:
            List[Dict[str, Any]]: Список модулей в структурированном виде
        """
        try:
            # Упрощенная логика извлечения модулей, 
            # в реальном приложении здесь должен быть более сложный парсинг
            modules = []
            lines = text.strip().split('\n')
            current_module = {}
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                if "Модуль" in line and ":" in line:
                    # Новый модуль
                    if current_module and "title" in current_module:
                        modules.append(current_module)
                    current_module = {"title": line.split(":", 1)[1].strip()}
                elif "Описание" in line and ":" in line and current_module:
                    current_module["description"] = line.split(":", 1)[1].strip()
                elif "Ключевые темы" in line and ":" in line and current_module:
                    topics_str = line.split(":", 1)[1].strip()
                    current_module["topics"] = [t.strip() for t in topics_str.split(",")]
                elif "Время" in line and ":" in line and current_module:
                    current_module["estimated_time"] = line.split(":", 1)[1].strip()
            
            # Добавляем последний модуль
            if current_module and "title" in current_module:
                modules.append(current_module)
                
            # Если не удалось извлечь модули, создаем заглушку
            if not modules:
                modules = [
                    {
                        "title": "Введение в нейросети",
                        "description": "Базовые концепции и принципы работы",
                        "topics": ["Основы ИИ", "Типы нейросетей", "Области применения"],
                        "estimated_time": "1-2 недели"
                    }
                ]
                
            return modules
            
        except Exception as e:
            logger.error(f"Ошибка при извлечении модулей из плана: {e}")
            return [
                {
                    "title": "Модуль 1: Введение в нейросети",
                    "description": "Не удалось правильно распарсить план",
                    "topics": ["Основы ИИ"],
                    "estimated_time": "1-2 недели"
                }
            ]
    
    def register_step_handlers(self, step_handlers: Dict[str, callable]):
        """
        Регистрирует обработчики специальных типов шагов
        
        Args:
            step_handlers: Словарь обработчиков шагов сценария
        """
        step_handlers["process_user_profile"] = self.process_user_profile
        step_handlers["process_learning_plan"] = self.process_learning_plan
        logger.info("Зарегистрированы обработчики шагов для LearningPlanPlugin") 