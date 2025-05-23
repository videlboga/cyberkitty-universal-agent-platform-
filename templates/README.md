# Шаблоны сценариев Universal Agent Platform

Коллекция готовых шаблонов сценариев для быстрого старта и обучения.

## 📁 Структура шаблонов

| Шаблон | Описание | Сложность | Плагины |
|--------|----------|-----------|---------|
| [user_registration](user_registration/) | Регистрация пользователя с настраиваемыми полями | 🟢 Простой | MongoDB |
| [llm_chat](llm_chat/) | Умный чат-бот с контекстом пользователя | 🟡 Средний | LLM, MongoDB |
| [llm_multi_step](llm_multi_step/) | LLM с разными моделями на каждом шаге | 🟡 Средний | LLM, MongoDB |
| [faq_rag](faq_rag/) | FAQ бот с семантическим поиском | 🟡 Средний | RAG, LLM |
| [orchestrator](orchestrator/) | Оркестратор других сценариев | 🔴 Сложный | Orchestrator, All |
| [scheduler](scheduler/) | Планировщик отложенных запусков | 🔴 Сложный | Scheduler |

## 🚀 Быстрый старт

### 1. Скопируйте шаблон
```bash
cp -r templates/user_registration scenarios/my_registration
```

### 2. Настройте сценарий
```bash
nano scenarios/my_registration/scenario.json
```

### 3. Создайте агента
```bash
curl -X POST http://localhost:8000/agents \
  -H "Content-Type: application/json" \
  -d @templates/user_registration/agent_config.json
```

### 4. Запустите сценарий
```bash
curl -X POST http://localhost:8000/agents/{agent_id}/execute
```

## 📚 Категории шаблонов

### 🟢 Базовые шаблоны
- **user_registration**: Сбор и валидация данных пользователя
- Идеально для начинающих
- Демонстрирует основные типы шагов

### 🟡 LLM интеграции  
- **llm_chat**: Персонализированный чат-бот
- **llm_multi_step**: Комплексные LLM процессы
- **faq_rag**: Семантический поиск + LLM ответы

### 🔴 Продвинутые системы
- **orchestrator**: Управление множественными сценариями
- **scheduler**: Отложенные и периодические запуски

## 🔧 Настройка шаблонов

### Изменение контекста
```json
{
  "initial_context": {
    "greeting": "Ваше приветствие",
    "collection_name": "your_collection"
  }
}
```

### Настройка плагинов
```json
{
  "plugins": ["MongoDBPlugin", "LLMPlugin"],
  "llm_model": "gpt-4",
  "temperature": 0.7
}
```

## 📊 Мониторинг и логи

Все шаблоны автоматически логируют:
- Начало и завершение выполнения
- Ошибки и исключения  
- Пользовательские взаимодействия
- Результаты LLM запросов

Логи доступны в:
```
logs/agent_launch.log
logs/llm_integration.log  
logs/errors.log
```

## 🔗 Связанные компоненты

### Плагины
- `MongoDBPlugin` - CRUD операции с БД
- `LLMPlugin` - Интеграция с языковыми моделями
- `RAGPlugin` - Семантический поиск
- `TelegramPlugin` - Telegram интеграция
- `SchedulerPlugin` - Планирование задач
- `OrchestratorPlugin` - Управление сценариями

### API эндпоинты
- `POST /agents` - Создание агента
- `POST /agents/{id}/execute` - Запуск сценария
- `GET /agents/{id}/status` - Статус выполнения
- `GET /scenarios` - Список сценариев

## 💡 Примеры использования

### Простая регистрация
```bash
# Создать агента с шаблоном регистрации
curl -X POST http://localhost:8000/agents \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Регистратор",
    "scenario_id": "template_user_registration"
  }'
```

### Комплексный процесс
```bash
# Запустить оркестратор для полного цикла
curl -X POST http://localhost:8000/agents \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Полный процесс", 
    "scenario_id": "template_orchestrator"
  }'
```

### Планирование задач
```bash
# Настроить отложенный запуск
curl -X POST http://localhost:8000/agents \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Планировщик",
    "scenario_id": "template_scheduler"
  }'
```

## 🛠️ Создание собственных шаблонов

1. **Скопируйте базовый шаблон**
2. **Измените scenario.json** - логику сценария
3. **Обновите README.md** - документацию
4. **Создайте agent_config.json** - конфигурацию агента
5. **Протестируйте** через API или unit тесты

## 📈 Метрики и аналитика

Шаблоны автоматически собирают метрики:
- Время выполнения сценариев
- Успешность завершения
- Популярность использования
- Ошибки и их частота

Данные доступны через:
```bash
# Статистика по шаблонам
curl http://localhost:8000/analytics/templates

# Метрики выполнения
curl http://localhost:8000/analytics/execution
```

## 🔒 Безопасность

- Все шаблоны используют валидацию входных данных
- Логирование подозрительных активностей
- Rate limiting для предотвращения злоупотреблений
- Изоляция выполнения сценариев

## 🤝 Вклад в развитие

Для добавления новых шаблонов:
1. Создайте папку в `templates/`
2. Добавьте `scenario.json`, `README.md`, `agent_config.json`
3. Обновите этот файл с описанием
4. Создайте pull request

---

**💡 Совет**: Начните с простых шаблонов (`user_registration`) и постепенно переходите к сложным (`orchestrator`).

📧 **Поддержка**: [GitHub Issues](https://github.com/yourusername/universal-agent-platform/issues)  
📖 **Документация**: [docs/scenario_format.md](../docs/scenario_format.md) 