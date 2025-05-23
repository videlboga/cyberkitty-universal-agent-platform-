# Universal Agent Platform - MVP

## Быстрый запуск MVP

1. **Клонируйте репозиторий:**
   ```bash
   git clone https://github.com/yourusername/universal_agent_system.git
   cd universal_agent_system
   ```

2. **Настройте переменные окружения:**
   ```bash
   cp .env.example .env
   # Отредактируйте .env согласно вашим требованиям
   ```

3. **Запустите с Docker:**
   ```bash
   docker-compose up -d
   ```

   После запуска:
   - API доступен по адресу: http://localhost:8000
   - Swagger документация: http://localhost:8000/docs
   - MongoDB доступна на порте 27017
   - Redis доступен на порте 6380
   - Telegram-бот запущен автоматически

4. **Проверьте работоспособность:**
   ```bash
   # Проверка API
   curl http://localhost:8000/health
   
   # Проверка Telegram-бота
   curl http://localhost:8000/integration/telegram/health
   
   # Проверка RAG-интеграции
   curl -X POST http://localhost:8000/integration/rag/query \
     -H "Content-Type: application/json" \
     -d '{"query": "Что такое RAG?"}'
   ```

5. **Используйте Telegram-бота:**
   - Найдите бота в Telegram по имени из .env
   - Отправьте команду /start для начала работы
   - Выберите агента через меню

## MVP Возможности
- Базовая работа с коллекциями (CRUD)
- Интеграция с Telegram
- Простые агенты и сценарии
- Интеграция с внешним RAG-сервисом
- Healthcheck эндпоинты
- Логирование всех действий

---

# Universal Agent Platform

## Быстрый старт
(см. выше)

## Примеры curl-запросов к API

### User
```bash
# Создать пользователя
curl -X POST http://localhost:8000/users/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Test User", "email": "testuser@example.com"}'

# Получить список пользователей
curl http://localhost:8000/users/

# Получить пользователя по id
curl http://localhost:8000/users/<user_id>

# Обновить пользователя
curl -X PATCH http://localhost:8000/users/<user_id> \
  -H "Content-Type: application/json" \
  -d '{"name": "Updated User"}'

# Удалить пользователя
curl -X DELETE http://localhost:8000/users/<user_id>
```

### Agent
```bash
# Создать агента
curl -X POST http://localhost:8000/agents/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Agent", "config": {"role": "assistant"}}'

# Получить список агентов
curl http://localhost:8000/agents/

# Получить агента по id
curl http://localhost:8000/agents/<agent_id>

# Обновить агента
curl -X PATCH http://localhost:8000/agents/<agent_id> \
  -H "Content-Type: application/json" \
  -d '{"name": "Updated Agent"}'

# Удалить агента
curl -X DELETE http://localhost:8000/agents/<agent_id>
```

### Scenario
```bash
# Создать сценарий
curl -X POST http://localhost:8000/scenarios/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Scenario", "steps": [{"type": "message", "text": "Hello"}]}'

# Получить список сценариев
curl http://localhost:8000/scenarios/

# Получить сценарий по id
curl http://localhost:8000/scenarios/<scenario_id>

# Обновить сценарий
curl -X PATCH http://localhost:8000/scenarios/<scenario_id> \
  -H "Content-Type: application/json" \
  -d '{"name": "Updated Scenario"}'

# Удалить сценарий
curl -X DELETE http://localhost:8000/scenarios/<scenario_id>
```

### Integration (mock)
```bash
# LLM mock
curl -X POST http://localhost:8000/integration/llm/query \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello, LLM!"}'

# RAG mock
curl -X POST http://localhost:8000/integration/rag/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Find info"}'

# amoCRM mock (универсальный endpoint для amoCRM)
curl -X POST http://localhost:8000/integration/crm/amocrm/query \
  -H "Content-Type: application/json" \
  -d '{"action": "create_lead", "data": {"name": "Test"}}'

# (Для обратной совместимости)
curl -X POST http://localhost:8000/integration/crm/query \
  -H "Content-Type: application/json" \
  -d '{"action": "create_lead", "data": {"name": "Test"}}'

# Новости (mock)
curl http://localhost:8000/integration/news/latest
curl "http://localhost:8000/integration/news/search?query=AI"

# Web Search (плагин, API будет добавлен)
# curl http://localhost:8000/integration/websearch/query?query=OpenAI

# Telegram (плагин, API будет добавлен)
# curl -X POST http://localhost:8000/integration/telegram/send -d '{"chat_id":123,"text":"Привет!"}'

# Получить список моделей OpenRouter
curl http://localhost:8000/integration/llm/models

# Получить структуру полей amoCRM (например, для сделок)
curl "http://localhost:8000/integration/crm/amocrm/fields?entity=leads"
# Для контактов: entity=contacts, для компаний: entity=companies
# Ответ: id, name, type, code, enums (варианты для списков), is_required, is_system, origin
# Пример:
# [
#   {"id": 123, "name": "Телефон", "type": "phone", ...},
#   {"id": 456, "name": "Статус", "type": "select", "enums": [{"id": 1, "value": "Первичный контакт"}, ...]}
# ]
```

**Интеграции расширяемы:**
- Для каждой CRM будет свой endpoint: `/integration/crm/<название>/query`
- Аналогично для других сервисов: `/integration/websearch/query`, `/integration/telegram/send` и т.д.
- Все плагины реализованы в `app/plugins/` и легко расширяются для реальных сервисов.

### OpenRouter: реальный запрос к LLM
```bash
curl -X POST http://localhost:8000/integration/llm/query \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Придумай смешную шутку про котов.",
    "use_openrouter": true,
    "model": "openai/gpt-3.5-turbo",  # или любую из /llm/models
    "max_tokens": 128
  }'
```

### Agent Scenario Run
```bash
# Запустить сценарий для агента
curl -X POST http://localhost:8000/agents/<agent_id>/run \
  -H "Content-Type: application/json" \
  -d '{"input": {"user_message": "Привет!"}}'
```

### Agent Scenario Step (переход по шагу)
```bash
# Перейти к следующему шагу сценария агента (с передачей состояния и context)
curl -X POST http://localhost:8000/agents/<agent_id>/step \
  -H "Content-Type: application/json" \
  -d '{
    "input_data": {"x": 5},
    "state": {"step_index": 1},
    "context": {"x": 5}
  }'
```

## Сложные сценарии: условия, ветвления, переменные

- Платформа поддерживает сценарии с условиями (`condition`), ветвлениями (`branches`), пользовательским контекстом (`context`) и явными переходами (`next_step`).
- Пример сложного сценария: [docs/examples/branching_scenario.json](docs/examples/branching_scenario.json)
- Описание формата сценария: [docs/scenario_format.md](docs/scenario_format.md)

### Integration (RAG через внешний сервис)
```bash
# Поиск через внешний RAG
curl -X POST http://localhost:8000/integration/rag/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Что такое RAG?", "top_k": 3}'
```

**RAG_URL** — адрес внешнего сервиса (по умолчанию http://rag.cyberkitty.tech/api)

**Формат запроса к внешнему RAG:**
```json
{
  "data": ["Ваш запрос", количество_результатов],
  "fn_index": 0,
  "session_hash": "уникальный_идентификатор"
}
```

**Пример ответа:**
```json
{
  "result": "...текст ответа из RAG...",
  "input": {"query": "Что такое RAG?"}
}
```

## Локальная разработка без Docker (venv)

1. **Создайте виртуальное окружение и активируйте его:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Установите зависимости:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. **Запустите MongoDB и Redis:**
   - Если сервисы установлены локально, убедитесь, что они работают:
     - MongoDB: `sudo systemctl start mongod` или `mongod --dbpath <путь>`
     - Redis: `redis-server`
   - Если нет — можно запустить только базы через docker-compose:
     ```bash
     docker-compose up mongo redis
     ```

4. **Создайте файл .env:**
   ```bash
   cp .env.example .env
   ```
   Проверьте, чтобы переменные указывали на локальные сервисы:
   ```
   MONGO_URI=mongodb://localhost:27017/universal_agent
   REDIS_URL=redis://localhost:6379/0
   ```

5. **Запустите FastAPI-приложение:**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

6. **(Опционально) Запустите Celery worker:**
   ```bash
   celery -A app.worker worker --loglevel=info
   ```
   (если есть задачи для Celery)

---

**Для быстрого старта можно использовать скрипт:**

```bash
#!/bin/bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env 2>/dev/null || true
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

**Преимущества:**
- Быстрый цикл разработки
- Удобная отладка
- Не требуется пересборка Docker-образа

**Для production и CI/CD используйте Docker!**

### Collections (универсальные коллекции/таблицы)
```bash
# Создать коллекцию
curl -X POST http://localhost:8000/db/collections/ \
  -H "Content-Type: application/json" \
  -d '{"name": "my_collection"}'

# Получить список коллекций
curl http://localhost:8000/db/collections/

# Добавить документ в коллекцию
curl -X POST http://localhost:8000/db/collections/my_collection/items \
  -H "Content-Type: application/json" \
  -d '{"field1": "value1", "field2": 123}'

# Получить все документы коллекции
curl http://localhost:8000/db/collections/my_collection/items

# Получить документ по id
curl http://localhost:8000/db/collections/my_collection/items/<item_id>

# Обновить документ
curl -X PATCH http://localhost:8000/db/collections/my_collection/items/<item_id> \
  -H "Content-Type: application/json" \
  -d '{"field1": "new_value"}'

# Удалить документ
curl -X DELETE http://localhost:8000/db/collections/my_collection/items/<item_id>
```

### Telegram (интеграция)
```bash
# Проверить работоспособность Telegram-бота (healthcheck)
curl http://localhost:8000/integration/telegram/health

# Отправить сообщение в Telegram
curl -X POST http://localhost:8000/integration/telegram/send \
  -H "Content-Type: application/json" \
  -d '{"chat_id":123456789,"text":"Привет из Universal Agent Platform!"}'
```

**Описание:**
- Для работы Telegram-интеграции необходимо указать токен бота в конфиге backend (см. app/api/integration.py, Application.builder().token(...)).
- Endpoint `/integration/telegram/health` проверяет доступность Telegram-бота через get_me.
- Endpoint `/integration/telegram/send` отправляет сообщение в указанный chat_id.
- Все логи интеграции пишутся в logs/llm_integration.log и logs/integration/telegram_send_test.log. 

## Менеджер агентов

Платформа поддерживает систему мультиагентов через `AgentManagerPlugin`, который позволяет переключаться между различными агентами в рамках одного диалога.

```bash
# Получить доступные агенты из менеджера агентов
curl -X GET "http://localhost:8000/agents/available" -H "Content-Type: application/json"

# Запустить сценарий меню агентов
curl -X POST "http://localhost:8000/agent-actions/manager/run" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "input_data": {
      "message": "start"
    }
  }'
```

## Система уведомлений

Платформа включает планировщик задач для отправки регулярных уведомлений.

```bash
# Проверить статус планировщика
curl -X GET "http://localhost:8000/scheduler/status" -H "Content-Type: application/json"

# Запустить планировщик
curl -X POST "http://localhost:8000/scheduler/start" -H "Content-Type: application/json"

# Остановить планировщик
curl -X POST "http://localhost:8000/scheduler/stop" -H "Content-Type: application/json"

# Отправить тестовое уведомление
curl -X POST "http://localhost:8000/scheduler/test-notification" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "agent_id": "lifehacker",
    "message": "Тестовое уведомление от системы"
  }'
```

## Мультиагентная система обучения

Платформа реализует комплексную систему обучения с несколькими специализированными агентами:

1. **Коуч** - помогает с рефлексией по прогрессу обучения, анализирует успехи и дает рекомендации
2. **Лайфхакер** - делится полезными советами по работе с нейросетями и инструментами ИИ
3. **Ментор** - отвечает на вопросы по теории и практике нейросетей, использует RAG для точных ответов
4. **Дайджест** - присылает релевантные новости и обновления из мира нейросетей
5. **Эксперт** - помогает с решением конкретных задач и проектов

Все агенты управляются через единый интерфейс `AgentManagerPlugin`, который позволяет:
- Переключаться между агентами в рамках одного диалога
- Сохранять контекст общения при переключении
- Возвращаться в главное меню агентов
- Получать персонализированные ответы от каждого агента

```bash
# Запустить сценарий менеджера агентов
curl -X POST "http://localhost:8000/agent-actions/manager/run" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "input_data": {
      "message": "start"
    }
  }'
```

## Типы поддерживаемых шагов в сценариях

Платформа поддерживает различные типы шагов в сценариях:

- **message** - отображение текстового сообщения
- **input** - получение ввода от пользователя
- **branch** - условное ветвление сценария
- **rag_search** - поиск информации через RAG
- **telegram_message** - отправка сообщения через Telegram
- **process_user_profile** - обработка профиля пользователя
- **generate_learning_plan** - генерация плана обучения
- **agent_menu** - меню выбора агентов
- **switch_agent** - переключение на другого агента
- **return_to_menu** - возврат в главное меню агентов

Все сценарии исполняются через `ScenarioExecutor`, который координирует работу плагинов и обработчиков шагов. 

## API Endpoints

### Пользователи (`/users`)
- `POST /users/` - Создание пользователя
- `GET /users/` - Список пользователей
- `GET /users/{user_id}` - Получение пользователя по ID
- `DELETE /users/{user_id}` - Удаление пользователя

### Сценарии (`/scenarios`)
- `POST /scenarios/` - Создание/обновление сценария
- `GET /scenarios/` - Список сценариев
- `GET /scenarios/{scenario_id}` - Получение сценария по ID
- `DELETE /scenarios/{scenario_id}` - Удаление сценария

### Агенты (`/agents`)
- `POST /agents/` - Создание агента
- `GET /agents/` - Список агентов
- `GET /agents/{agent_id}` - Получение агента по ID

### Планировщик (`/scheduler`)
- `GET /scheduler/status` - Статус планировщика
- `POST /scheduler/start` - Запуск планировщика
- `POST /scheduler/stop` - Остановка планировщика
- `POST /scheduler/test-notification` - Тестовое уведомление
- `POST /scheduler/tasks` - Создание задачи

### Интеграции (`/integration`)
- `GET /integration/llm/models` - Список моделей LLM
- `POST /integration/llm/query` - Запрос к LLM
- `POST /integration/crm/query` - Запрос к CRM
- `POST /integration/crm/amocrm/query` - Запрос к amoCRM
- `POST /integration/telegram/send` - Отправка сообщения в Telegram
- `POST /integration/telegram/send_test` - Тестовая отправка в Telegram
- `POST /integration/mongodb/save_test` - Тестовое сохранение в MongoDB

### Коллекции (`/db/collections`)
- `POST /db/collections/` - Создание коллекции
- `GET /db/collections/` - Список коллекций
- `POST /db/collections/{name}/items` - Создание документа
- `GET /db/collections/{name}/items` - Список документов
- `GET /db/collections/{name}/items/{item_id}` - Получение документа
- `PATCH /db/collections/{name}/items/{item_id}` - Обновление документа
- `DELETE /db/collections/{name}/items/{item_id}` - Удаление документа

### Обучение (`/learning`)
- `POST /learning/onboard` - Запуск онбординга пользователя

### Запуск сценариев (`/runner`)
- `POST /runner/{agent_id}/execute` - Выполнение сценария 

## Примеры использования API

### Создание пользователя
```bash
curl -X POST "http://localhost:8000/users/" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "first_name": "Иван",
    "last_name": "Иванов",
    "username": "ivan"
  }'
```

### Создание сценария
```bash
curl -X POST "http://localhost:8000/scenarios/" \
  -H "Content-Type: application/json" \
  -d '{
    "scenario_id": "onboarding",
    "name": "Онбординг пользователя",
    "description": "Сценарий для первичного знакомства с платформой",
    "steps": [
      {
        "type": "message",
        "content": "Добро пожаловать! Я помогу вам начать работу с платформой."
      }
    ]
  }'
```

### Создание агента
```bash
curl -X POST "http://localhost:8000/agents/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Менеджер",
    "description": "Агент для управления задачами",
    "scenario_id": "task_manager"
  }'
```

### Запуск планировщика
```bash
curl -X POST "http://localhost:8000/scheduler/start"
```

### Создание задачи в планировщике
```bash
curl -X POST "http://localhost:8000/scheduler/tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "trigger_type": "once",
    "trigger_config": {
      "datetime": "2024-03-20T10:00:00Z"
    },
    "action_type": "send_notification",
    "action_config": {
      "text": "Напоминание о встрече"
    }
  }'
```

### Отправка сообщения через Telegram
```bash
curl -X POST "http://localhost:8000/integration/telegram/send" \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": "123456789",
    "text": "Привет! Это тестовое сообщение."
  }'
```

### Запуск онбординга
```bash
curl -X POST "http://localhost:8000/learning/onboard" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "chat_id": "123456789",
    "language": "ru",
    "first_name": "Иван",
    "last_name": "Иванов",
    "username": "ivan"
  }'
```

### Выполнение сценария
```bash
curl -X POST "http://localhost:8000/runner/manager/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "context": {
      "user_id": "user123",
      "chat_id": "123456789"
    }
  }' 
```

## Примеры минималистичных сценариев (JSON)

### 1. Приветствие в Telegram
```json
{
  "name": "Greeting Scenario",
  "steps": [
    {
      "id": "step1",
      "type": "plugin_action",
      "plugin": "TelegramPlugin",
      "action": "send_message",
      "params": {
        "chat_id": "{{ telegram_chat_id }}",
        "text": "Добро пожаловать!"
      },
      "result_var": "greeting_result"
    },
    {
      "id": "step2",
      "type": "end"
    }
  ],
  "initial_context": {
    "telegram_chat_id": "648981358"
  }
}
```

### 2. Ветвление по ответу пользователя
```json
{
  "name": "Branching Scenario",
  "steps": [
    {
      "id": "step1",
      "type": "plugin_action",
      "plugin": "TelegramPlugin",
      "action": "send_message",
      "params": {
        "chat_id": "{{ telegram_chat_id }}",
        "text": "Ты человек? (да/нет)"
      },
      "result_var": "ask_result"
    },
    {
      "id": "step2",
      "type": "plugin_action",
      "plugin": "TelegramPlugin",
      "action": "wait_for_reply",
      "params": {
        "chat_id": "{{ telegram_chat_id }}"
      },
      "result_var": "user_reply"
    },
    {
      "id": "step3",
      "type": "branch",
      "condition": "{{ user_reply.text | lower == 'да' }}",
      "true_next": "step4",
      "false_next": "step5"
    },
    {
      "id": "step4",
      "type": "plugin_action",
      "plugin": "TelegramPlugin",
      "action": "send_message",
      "params": {
        "chat_id": "{{ telegram_chat_id }}",
        "text": "Отлично, человек!"
      },
      "result_var": "final_result"
    },
    {
      "id": "step5",
      "type": "plugin_action",
      "plugin": "TelegramPlugin",
      "action": "send_message",
      "params": {
        "chat_id": "{{ telegram_chat_id }}",
        "text": "Жаль, что не человек :("
      },
      "result_var": "final_result"
    },
    {
      "id": "step6",
      "type": "end"
    }
  ],
  "initial_context": {
    "telegram_chat_id": "648981358"
  }
}
```

### 3. Переключение на другой сценарий
```json
{
  "name": "Switch Scenario",
  "steps": [
    {
      "id": "step1",
      "type": "plugin_action",
      "plugin": "TelegramPlugin",
      "action": "send_message",
      "params": {
        "chat_id": "{{ telegram_chat_id }}",
        "text": "Сейчас переключу тебя на другой сценарий!"
      },
      "result_var": "switch_msg"
    },
    {
      "id": "step2",
      "type": "switch_scenario",
      "params": {
        "new_scenario_id": "ANOTHER_SCENARIO_ID"
      }
    }
  ],
  "initial_context": {
    "telegram_chat_id": "648981358"
  }
}
```

### 4. Логирование и завершение
```json
{
  "name": "Log and End",
  "steps": [
    {
      "id": "step1",
      "type": "log",
      "params": {
        "level": "INFO",
        "message": "Сценарий стартовал!"
      }
    },
    {
      "id": "step2",
      "type": "end"
    }
  ]
}
```

### 5. Использование результата плагина в следующем шаге
```json
{
  "name": "Use Plugin Result",
  "steps": [
    {
      "id": "step1",
      "type": "plugin_action",
      "plugin": "SomePlugin",
      "action": "get_data",
      "params": {
        "param1": "value"
      },
      "result_var": "data_result"
    },
    {
      "id": "step2",
      "type": "plugin_action",
      "plugin": "TelegramPlugin",
      "action": "send_message",
      "params": {
        "chat_id": "{{ telegram_chat_id }}",
        "text": "Результат: {{ data_result.value }}"
      },
      "result_var": "send_result"
    },
    {
      "id": "step3",
      "type": "end"
    }
  ],
  "initial_context": {
    "telegram_chat_id": "648981358"
  }
}
``` 