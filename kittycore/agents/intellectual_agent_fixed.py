# Копируем только проблемную часть для исправления отступов
# Строки 950-984 исправленные:

    def _format_plan_for_memory(self, execution_plan: Dict) -> str:
        """Форматирование плана для сохранения в память"""
        formatted_steps = []
        for step in execution_plan.get('steps', []):
            step_text = f"Шаг {step.get('step', '?')}: {step.get('action', 'Неизвестное действие')}"
            step_text += f" (инструмент: {step.get('tool', 'неизвестно')})"
            formatted_steps.append(step_text)
        
        return '\n'.join(formatted_steps)
    
    def _extract_failure_reasons(self, result: Dict) -> str:
        """Извлечение причин неудач для обучения"""
        failures = []
        for step_result in result.get('step_results', []):
            if not step_result.get('success', True):
                error = step_result.get('error', 'Неизвестная ошибка')
                failures.append(f"- {error}")
        
        return '\n'.join(failures) if failures else "- Нет явных ошибок в шагах"
    
    def _generate_fallback_insights(self, task_description: str, analysis: Dict[str, Any]) -> str:
        """Генерация базовых инсайтов без A-MEM"""
        insights = "🧠 БАЗОВЫЕ ИНСАЙТЫ (A-MEM недоступен):\n\n"
        
        # Анализируем задачу и даём рекомендации
        if "анализ" in task_description.lower():
            insights += "📊 АНАЛИЗ ЗАДАЧ:\n"
            insights += "- Начинай с поиска актуальной информации (web_client)\n"
            insights += "- Создавай структурированные файлы (.json для данных, .md для отчётов)\n"
            insights += "- Включай конкретные цифры, названия, статистику\n\n"
        
        if "прототип" in task_description.lower() or "создай" in task_description.lower():
            insights += "🎨 СОЗДАНИЕ ПРОТОТИПОВ:\n"
            insights += "- Описывай конкретные UI элементы и функции\n"
            insights += "- Включай технические детали реализации\n"
            insights += "- Создавай работающий код, а не описания\n\n"
        
        if len(task_description.split()) > 15:  # Сложная задача
            insights += "⚡ СЛОЖНЫЕ ЗАДАЧИ:\n"
            insights += "- Разбивай на 4-8 шагов\n"
            insights += "- Каждый шаг = один конкретный результат\n"
            insights += "- Используй результаты предыдущих шагов в следующих\n\n"
        
        return insights 