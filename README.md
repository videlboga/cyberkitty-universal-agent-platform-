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
  -d '{"query": "Что такое RAG?"}'
```

**RAG_URL** — адрес внешнего сервиса (по умолчанию http://92.242.60.87:5002/api)

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