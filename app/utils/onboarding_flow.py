from typing import Dict, Any, List
import json

class OnboardingFlow:
    """
    Класс для управления сценарием первоначального опроса пользователя.
    Содержит шаги опроса, валидацию ответов и сохранение результатов.
    """
    
    # Определяем основные шаги опроса
    STEPS = {
        "start": {
            "message": "Привет! Я помогу вам создать индивидуальный план обучения нейросетям. Для этого задам несколько вопросов. Готовы начать?",
            "type": "confirmation",
            "next_step": "experience"
        },
        "experience": {
            "message": "Какой у вас опыт работы с нейросетями и искусственным интеллектом?",
            "type": "options",
            "options": [
                {"text": "Новичок (никогда не работал с нейросетями)", "value": "beginner"},
                {"text": "Начинающий (использовал готовые решения)", "value": "intermediate"},
                {"text": "Продвинутый (разрабатывал собственные проекты)", "value": "advanced"}
            ],
            "next_step": "interests"
        },
        "interests": {
            "message": "Какие области нейросетей вас интересуют больше всего? (выберите до 3 вариантов)",
            "type": "multiple_options",
            "options": [
                {"text": "Компьютерное зрение", "value": "computer_vision"},
                {"text": "Обработка естественного языка", "value": "nlp"},
                {"text": "Генеративные модели", "value": "generative_models"},
                {"text": "Рекомендательные системы", "value": "recommender_systems"},
                {"text": "Автоматизация бизнес-процессов", "value": "business_automation"},
                {"text": "Медицина и здравоохранение", "value": "healthcare"},
                {"text": "Финансы и трейдинг", "value": "finance"}
            ],
            "max_selections": 3,
            "next_step": "learning_goals"
        },
        "learning_goals": {
            "message": "Какие цели вы хотите достичь в изучении нейросетей?",
            "type": "multiple_options",
            "options": [
                {"text": "Понять основные принципы работы", "value": "understand_basics"},
                {"text": "Научиться использовать готовые решения", "value": "use_existing_solutions"},
                {"text": "Создавать собственные модели", "value": "create_own_models"},
                {"text": "Применять в своей профессиональной области", "value": "apply_professionally"},
                {"text": "Начать карьеру в области нейросетей", "value": "career_change"}
            ],
            "max_selections": 2,
            "next_step": "learning_style"
        },
        "learning_style": {
            "message": "Какой формат обучения вам больше подходит?",
            "type": "options",
            "options": [
                {"text": "Теоретический (статьи, книги, лекции)", "value": "theoretical"},
                {"text": "Практический (проекты, задачи, кейсы)", "value": "practical"},
                {"text": "Смешанный (теория + практика)", "value": "mixed"}
            ],
            "next_step": "available_time"
        },
        "available_time": {
            "message": "Сколько времени в неделю вы готовы уделять обучению?",
            "type": "options",
            "options": [
                {"text": "Менее 5 часов", "value": "less_than_5"},
                {"text": "5-10 часов", "value": "5_to_10"},
                {"text": "10-20 часов", "value": "10_to_20"},
                {"text": "Более 20 часов", "value": "more_than_20"}
            ],
            "next_step": "notifications"
        },
        "notifications": {
            "message": "Хотите ли вы получать уведомления с подсказками и рекомендациями?",
            "type": "options",
            "options": [
                {"text": "Да, ежедневно", "value": "daily"},
                {"text": "Да, еженедельно", "value": "weekly"},
                {"text": "Нет, только по запросу", "value": "on_demand"}
            ],
            "next_step": "finish"
        },
        "finish": {
            "message": "Спасибо за ответы! Теперь я создам для вас индивидуальный план обучения на основе ваших предпочтений.",
            "type": "message",
            "next_step": "generate_plan"
        },
        "generate_plan": {
            "message": "Ваш план обучения готов! Вот основные модули, которые рекомендую изучить:",
            "type": "plan_generation",
            "next_step": "introduction"
        },
        "introduction": {
            "message": "Теперь вы можете начать обучение или общаться с любым из наших специализированных агентов:\n\n• Коуч - поможет с рефлексией по прогрессу\n• Лайфхакер - поделится полезными советами\n• Ментор - ответит на вопросы\n• Дайджест - пришлет релевантные новости\n• Эксперт - поможет с решением конкретных задач",
            "type": "message",
            "next_step": "select_agent"
        },
        "select_agent": {
            "message": "С каким агентом хотите поговорить?",
            "type": "agent_selection",
            "next_step": None
        }
    }
    
    @staticmethod
    def get_step(step_name: str) -> Dict[str, Any]:
        """
        Получить информацию о шаге по его имени
        
        Args:
            step_name: Имя шага
            
        Returns:
            Dict[str, Any]: Информация о шаге или пустой словарь, если шаг не найден
        """
        return OnboardingFlow.STEPS.get(step_name, {})
    
    @staticmethod
    def get_next_step(current_step: str) -> str:
        """
        Получить имя следующего шага
        
        Args:
            current_step: Имя текущего шага
            
        Returns:
            str: Имя следующего шага или None, если следующего шага нет
        """
        step_info = OnboardingFlow.get_step(current_step)
        return step_info.get("next_step")
    
    @staticmethod
    def get_user_profile_from_answers(answers: Dict[str, Any]) -> Dict[str, Any]:
        """
        Преобразовать ответы пользователя в профиль
        
        Args:
            answers: Словарь с ответами пользователя
            
        Returns:
            Dict[str, Any]: Профиль пользователя на основе ответов
        """
        profile = {}
        
        # Опыт
        if "experience" in answers:
            experience_map = {
                "beginner": "начинающий",
                "intermediate": "средний",
                "advanced": "продвинутый"
            }
            profile["experience_level"] = experience_map.get(answers["experience"], "начинающий")
        
        # Интересы
        if "interests" in answers and isinstance(answers["interests"], list):
            interests_map = {
                "computer_vision": "Компьютерное зрение",
                "nlp": "Обработка естественного языка",
                "generative_models": "Генеративные модели",
                "recommender_systems": "Рекомендательные системы",
                "business_automation": "Автоматизация бизнес-процессов",
                "healthcare": "Медицина и здравоохранение",
                "finance": "Финансы и трейдинг"
            }
            profile["interests"] = [interests_map.get(interest, interest) for interest in answers["interests"]]
        
        # Цели обучения
        if "learning_goals" in answers and isinstance(answers["learning_goals"], list):
            goals_map = {
                "understand_basics": "Понимание основных принципов",
                "use_existing_solutions": "Использование готовых решений",
                "create_own_models": "Создание собственных моделей",
                "apply_professionally": "Применение в профессиональной области",
                "career_change": "Начало карьеры в нейросетях"
            }
            profile["learning_goals"] = [goals_map.get(goal, goal) for goal in answers["learning_goals"]]
        
        # Стиль обучения
        if "learning_style" in answers:
            style_map = {
                "theoretical": "теоретический",
                "practical": "практический",
                "mixed": "смешанный"
            }
            profile["preferred_learning_style"] = style_map.get(answers["learning_style"], "смешанный")
        
        # Доступное время
        if "available_time" in answers:
            time_map = {
                "less_than_5": "менее 5 часов",
                "5_to_10": "5-10 часов",
                "10_to_20": "10-20 часов",
                "more_than_20": "более 20 часов"
            }
            profile["available_time_per_week"] = time_map.get(answers["available_time"], "5-10 часов")
        
        # Уведомления
        if "notifications" in answers:
            notifications_enabled = answers["notifications"] != "none"
            profile["notifications_enabled"] = notifications_enabled
            
            if answers["notifications"] == "daily":
                profile["notification_frequency"] = "daily"
            elif answers["notifications"] == "weekly":
                profile["notification_frequency"] = "weekly"
            else:
                profile["notification_frequency"] = "on_demand"
        
        return profile 