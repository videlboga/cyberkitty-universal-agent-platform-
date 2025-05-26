# Шаблоны сценариев KittyCore Universal Agent Platform

Коллекция готовых шаблонов сценариев для быстрого старта и обучения.

## 📁 Структура шаблонов

### 🧩 Атомарные сценарии
| Сценарий | Описание | Плагины | Сложность |
|----------|----------|---------|-----------|
| [atomic/](atomic/) | **10 атомарных блоков** для композиции | Различные | 🟢 Простые |
| `telegram_send_message` | Отправка сообщения в Telegram | SimpleTelegramPlugin | 🟢 |
| `telegram_send_buttons` | Отправка сообщения с кнопками | SimpleTelegramPlugin | 🟢 |
| `llm_query` | Запрос к языковой модели | SimpleLLMPlugin | 🟡 |
| `mongo_save_data` | Сохранение данных в MongoDB | MongoPlugin | 🟢 |
| `mongo_find_data` | Поиск данных в MongoDB | MongoPlugin | 🟢 |
| `rag_search` | Семантический поиск в базе знаний | SimpleRAGPlugin | 🟡 |
| `conditional_branch` | Условное ветвление | Core Engine | 🟡 |
| `switch_scenario` | Переключение сценариев | Core Engine | 🟡 |
| `scheduler_create_task` | Создание отложенной задачи | SimpleSchedulerPlugin | 🟡 |
| `log_message` | Логирование сообщений | Core Engine | 🟢 |

### 🏗️ Композитные сценарии
| Шаблон | Описание | Сложность | Плагины |
|--------|----------|-----------|---------|
| [user_registration](user_registration/) | Регистрация пользователя с настраиваемыми полями | 🟡 Средний | MongoDB, Telegram |
| [llm_chat](llm_chat/) | Умный чат-бот с контекстом пользователя | 🟡 Средний | LLM, MongoDB, Telegram |
| [llm_multi_step](llm_multi_step/) | LLM с разными моделями на каждом шаге | 🟡 Средний | LLM, MongoDB |
| [faq_rag](faq_rag/) | FAQ бот с семантическим поиском | 🟡 Средний | RAG, LLM, Telegram |
| [orchestrator](orchestrator/) | Оркестратор других сценариев | 🔴 Сложный | All Plugins |
| [scheduler](scheduler/) | Планировщик отложенных запусков | 🔴 Сложный | Scheduler, Telegram |

## 🚀 Быстрый старт

### 1. Атомарный сценарий (простой)
```bash
# Отправить сообщение в Telegram
curl -X POST http://localhost:8000/simple/execute \
  -H "Content-Type: application/json" \
  -d '{
    "scenario_id": "atomic_telegram_send_message",
    "context": {
      "chat_id": "123456789",
      "text": "Привет из KittyCore!"
    }
  }'
```

### 2. Композитный сценарий (сложный)
```bash
# Скопировать и настроить шаблон
cp -r templates/user_registration scenarios/my_registration
nano scenarios/my_registration/scenario.json

# Выполнить через API
curl -X POST http://localhost:8000/simple/channels/telegram_bot/execute \
  -H "Content-Type: application/json" \
  -d '{
    "scenario_id": "user_registration",
    "context": {
      "user_id": "123456789",
      "chat_id": "123456789"
    }
  }'
```

### 3. Создание композиции из атомарных
```bash
# Создать новый сценарий из атомарных блоков
cat > scenarios/my_composite.json << 'EOF'
{
  "scenario_id": "my_welcome_flow",
  "steps": [
    {
      "id": "start",
      "type": "start",
      "next_step": "log_start"
    },
    {
      "id": "log_start",
      "type": "switch_scenario",
      "params": {
        "target_scenario": "atomic_log_message",
        "context_updates": {
          "message": "Начинаем приветствие пользователя {user_name}",
          "level": "INFO"
        }
      },
      "next_step": "send_welcome"
    },
    {
      "id": "send_welcome",
      "type": "switch_scenario",
      "params": {
        "target_scenario": "atomic_telegram_send_message",
        "context_updates": {
          "text": "Добро пожаловать, {user_name}!"
        }
      },
      "next_step": "end"
    },
    {
      "id": "end",
      "type": "end"
    }
  ]
}
EOF
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