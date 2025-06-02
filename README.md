# 🎯 Universal Agent Platform (KittyCore)

**Универсальная платформа для создания ИИ-агентов**

**Принцип:** ПРОСТОТА ПРЕВЫШЕ ВСЕГО! 

## 🏗️ Упрощённая архитектура

```
SimpleScenarioEngine (единственный движок)
├── Базовые обработчики (start, end, action, input, branch, switch_scenario, log_message)
├── ChannelManager (управление каналами и полингом)
└── Плагин-специфичные обработчики (102+ handlers):
    ├── MongoPlugin (mongo_insert_document, mongo_find_documents, mongo_update_document, etc.)
    ├── SimpleLLMPlugin (llm_query, llm_chat)
    ├── SimpleRAGPlugin (rag_search, rag_answer)
    ├── SimpleSchedulerPlugin (scheduler_create_task, scheduler_list_tasks, etc.)
    ├── SimpleHTTPPlugin (http_get, http_post, http_put, http_delete, http_request)
    ├── SimpleAmoCRMPlugin (amocrm_find_contact, amocrm_create_contact, amocrm_create_lead, etc.)
    └── ChannelActions (channel_action для Telegram операций)

Simple API (app/api/simple.py) - Порт 8085
├── POST /api/v1/simple/channels/{channel_id}/execute (основной endpoint)
├── GET /health (быстрая проверка)
├── GET /api/v1/simple/health (полная проверка здоровья)
├── GET /api/v1/simple/info (информация о системе и плагинах)
├── GET /api/v1/simple/channels (список каналов)
├── POST /api/v1/simple/channels/{channel_id}/start (запуск канала)
├── POST /api/v1/simple/mongo/* (MongoDB операции)
└── POST /api/v1/simple/execute (выполнение отдельного шага)
```

## 🎯 Принципы архитектуры

1. ✅ **Один движок** - `SimpleScenarioEngine` вместо множества
2. ✅ **ChannelManager** - автоматическое управление каналами и полингом
3. ✅ **Простая система плагинов** - все наследуют `BasePlugin`
4. ✅ **Минимум API endpoints** - основной функционал через один endpoint
5. ✅ **YAML сценарии** - поддержка современного YAML формата
6. ✅ **Явная передача контекста** - контекст передается между компонентами
7. ✅ **Разделение ответственности** - движок универсален, плагины специализированы

## 📁 Структура проекта

```
app/
├── core/
│   ├── simple_engine.py          # Единственный движок выполнения
│   ├── base_plugin.py            # Базовый класс для всех плагинов
│   ├── channel_manager.py        # Управление каналами
│   ├── plugin_manager.py         # Управление плагинами
│   ├── logging_config.py         # Конфигурация логирования
│   └── utils.py                  # Утилиты
├── plugins/
│   ├── simple_telegram_plugin.py # Telegram интеграция
│   ├── mongo_plugin.py           # MongoDB операции
│   ├── simple_llm_plugin.py      # LLM интеграция (OpenAI, Anthropic)
│   ├── simple_rag_plugin.py      # RAG поиск и индексация
│   ├── simple_scheduler_plugin.py # Планировщик задач
│   ├── simple_http_plugin.py     # HTTP клиент для внешних API
│   ├── simple_amocrm_plugin.py   # AmoCRM интеграция
│   └── plugin_template.py        # Шаблон для новых плагинов
├── api/
│   └── simple.py                 # Единый API
├── models.py                     # Pydantic модели
├── simple_dependencies.py       # Инициализация зависимостей
└── simple_main.py               # Главный файл запуска

scenarios/                        # JSON сценарии
tests/                           # Тесты
logs/                           # Логи (engine.log, plugins.log, api.log, errors.log)
docs/                           # Документация
```

## 🚀 Быстрый старт

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 2. Настройка переменных окружения

Создайте файл `.env`:

```bash
# Telegram (обязательно для Telegram функций)
TELEGRAM_BOT_TOKEN=your_bot_token

# MongoDB (опционально, по умолчанию используется локальная БД)
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DATABASE_NAME=universal_agent_platform

# LLM API ключи (опционально)
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key

# AmoCRM интеграция (опционально)
AMO_BASE_URL=https://your_domain.amocrm.ru
AMO_ACCESS_TOKEN=your_access_token

# Логирование
LOG_LEVEL=INFO

# API конфигурация
HOST=0.0.0.0
PORT=8085
```

### 3. Запуск системы

```bash
# Простой запуск
python app/simple_main.py

# Или через Docker
docker-compose -f docker-compose.simple.yml up

# Или через скрипт
./run_simple.sh
```

## 📋 API Endpoints

### Основной endpoint

**POST /api/v1/simple/channels/{channel_id}/execute**

Выполняет сценарий для указанного канала.

```json
{
  "user_id": "123456789",
  "chat_id": "987654321", 
  "context": {
    "user_name": "Пользователь",
    "message_text": "/start"
  },
  "scenario_id": "optional_specific_scenario"
}
```

**Response:**
```json
{
  "success": true,
  "scenario_id": "simple_telegram",
  "final_context": {...},
  "message": "Сценарий выполнен успешно"
}
```

### Служебные endpoints

- **GET /health** - Быстрая проверка
- **GET /api/v1/simple/health** - Полная проверка здоровья системы
- **GET /api/v1/simple/info** - Информация о системе и плагинах
- **GET /api/v1/simple/channels** - Список каналов
- **POST /api/v1/simple/channels/{channel_id}/start** - Запуск канала
- **POST /api/v1/simple/mongo/*** - MongoDB операции
- **POST /api/v1/simple/execute** - Выполнение отдельного шага

## 🎬 Типы шагов сценариев

### Базовые (в SimpleScenarioEngine):
- `start` - Начало сценария
- `end` - Завершение сценария  
- `action` - Выполнение действий
- `input` - Ожидание ввода пользователя
- `branch` - Условная логика с ветвлением
- `switch_scenario` - Переключение на другой сценарий
- `log_message` - Логирование сообщений

### Каналы (ChannelManager):
- `channel_action` - Универсальное действие канала:
  - `action: send_message` - Отправка сообщений
  - `action: send_buttons` - Отправка inline кнопок  
  - `action: edit_message` - Редактирование сообщений

### MongoDB (MongoPlugin):
- `mongo_insert_document` - Вставка документа
- `mongo_upsert_document` - Вставка или обновление
- `mongo_find_documents` - Поиск документов
- `mongo_find_one_document` - Поиск одного документа
- `mongo_update_document` - Обновление документа
- `mongo_delete_document` - Удаление документа
- `mongo_save_scenario` - Сохранение сценария

### LLM (SimpleLLMPlugin):
- `llm_query` - Запрос к LLM
- `llm_chat` - Чат с LLM

### RAG (SimpleRAGPlugin):
- `rag_search` - Поиск в базе знаний
- `rag_answer` - Ответ на основе RAG поиска

### Планировщик (SimpleSchedulerPlugin):
- `scheduler_create_task` - Создание задачи
- `scheduler_list_tasks` - Список задач
- `scheduler_get_task` - Получение задачи
- `scheduler_cancel_task` - Отмена задачи
- `scheduler_get_stats` - Статистика планировщика

### HTTP клиент (SimpleHTTPPlugin):
- `http_get` - GET запрос к внешнему API
- `http_post` - POST запрос с данными
- `http_put` - PUT запрос для обновления
- `http_delete` - DELETE запрос
- `http_request` - Универсальный HTTP запрос

### AmoCRM (SimpleAmoCRMPlugin):
- `amocrm_find_contact` - Поиск контакта
- `amocrm_create_contact` - Создание контакта
- `amocrm_update_contact` - Обновление контакта
- `amocrm_find_lead` - Поиск сделки
- `amocrm_create_lead` - Создание сделки
- `amocrm_add_note` - Добавление заметки
- `amocrm_search` - Универсальный поиск
- И множество других AmoCRM операций (companies, tasks, advanced, admin)

## 📝 Пример YAML сценария

```yaml
scenario_id: likeprovodnik_init
description: "ЛайкПроводник - Главный сценарий инициализации"
version: "1.0"

initial_context:
  system_name: "ЛайкПроводник"
  version: "1.0"

steps:
  - id: start
    type: start
    next_step: welcome_message

  - id: welcome_message
    type: channel_action
    params:
      action: send_message
      chat_id: "{chat_id}"
      text: |
        🤖 **Привет! Я ЛайкПроводник** — твой AI-помощник!
        
        ✨ **Что я умею:**
        🎯 **AI-Путь** — создаю персональный план обучения
        💡 **Лайфхаки** — генерирую бизнес-советы с ИИ
        
        💬 **Просто напиши что тебя интересует!**
      parse_mode: HTML
    next_step: load_user_profile

  - id: load_user_profile
    type: mongo_find_one_document
    params:
      collection: users
      filter:
        user_id: "{user_id}"
      output_var: user_profile
    next_step: check_user_exists

  - id: check_user_exists
    type: branch
    params:
      conditions:
        - condition: "not context.get('user_profile') or not context.get('user_profile', {}).get('onboarding_completed')"
          next_step: start_onboarding
      default_next_step: go_to_router

  - id: start_onboarding
    type: switch_scenario
    params:
      target_scenario: ai_path_onboarding_flow
      preserve_context: true
    next_step: end

  - id: go_to_router
    type: switch_scenario
    params:
      target_scenario: likeprovodnik_main_router
      preserve_context: true
    next_step: end

  - id: end
    type: end
```

## 📡 Управление каналами

### Создание канала

```bash
# Создание Telegram канала
curl -X POST http://localhost:8085/api/v1/simple/mongo/insert \
  -H 'Content-Type: application/json' \
  -d '{
    "collection": "channels",
    "document": {
      "channel_id": "my_telegram_bot",
      "channel_type": "telegram",
      "name": "Мой Telegram Bot",
      "description": "Описание бота",
      "telegram_bot_token": "YOUR_BOT_TOKEN",
      "start_scenario_id": "my_init_scenario",
      "config": {
        "bot_token": "YOUR_BOT_TOKEN",
        "polling_enabled": true,
        "webhook_enabled": false
      },
      "status": "active"
    }
  }'
```

### Запуск канала

```bash
# Запуск канала (автоматически запускает полинг)
curl -X POST http://localhost:8085/api/v1/simple/channels/my_telegram_bot/start

# Список всех каналов
curl http://localhost:8085/api/v1/simple/channels

# Выполнение сценария в канале
curl -X POST http://localhost:8085/api/v1/simple/channels/my_telegram_bot/execute \
  -H 'Content-Type: application/json' \
  -d '{
    "user_id": "123456789",
    "chat_id": "987654321",
    "context": {
      "message_text": "/start"
    }
  }'
```

### Загрузка YAML сценариев

```python
#!/usr/bin/env python3
import requests
import yaml

# Загрузка YAML сценария
with open('scenarios/yaml/my_scenario.yaml', 'r', encoding='utf-8') as f:
    scenario = yaml.safe_load(f)

url = 'http://localhost:8085/api/v1/simple/mongo/save-scenario'
payload = {
    'collection': 'scenarios',
    'scenario_id': scenario['scenario_id'],
    'document': scenario
}

response = requests.post(url, json=payload)
print("✅ Сценарий загружен" if response.json().get('success') else "❌ Ошибка")
```

## 🧪 Тестирование

```bash
# Запуск всех тестов
pytest tests/

# Тест конкретного компонента
pytest tests/test_simple_engine.py

# Проверка здоровья системы
curl http://localhost:8085/health

# Информация о системе
curl http://localhost:8085/api/v1/simple/info

# Список каналов
curl http://localhost:8085/api/v1/simple/channels
```

## 📊 Логирование

Все логи сохраняются в папку `logs/` в JSON формате:

- `logs/engine.log` - Логи движка выполнения
- `logs/plugins.log` - Логи плагинов
- `logs/api.log` - Логи API запросов
- `logs/errors.log` - Логи ошибок
- `logs/tests.log` - Логи тестов

Конфигурация логирования в `app/core/logging_config.py`.

## 🔌 Создание плагинов

Для создания нового плагина:

1. Наследуйте `BasePlugin`
2. Реализуйте `register_handlers()` и `healthcheck()`
3. Добавьте плагин в `simple_dependencies.py`

Пример в `app/plugins/plugin_template.py`.

## 🐳 Docker

```bash
# Простой запуск
docker-compose -f docker-compose.simple.yml up

# С MongoDB
docker-compose up

# Только API
docker build -t kittycore .
docker run -p 8085:8085 kittycore
```

## 🚫 Что НЕ нужно восстанавливать

- Фронтенд (удален)
- Множественные движки (atomic, extensible, hybrid, unified)
- Сложные адаптеры и обёртки  
- Дублирующиеся API endpoints
- Избыточные сервисы
- Сложные системы зависимостей

## 📚 Документация

- `docs/api_documentation.md` - Подробная документация API
- `docs/scenario_format.md` - Формат сценариев
- `docs/NEW_PLUGIN_GUIDE.md` - Руководство по созданию плагинов
- `docs/scenario_development_guide.md` - Разработка сценариев

---

**Помните: Простота превыше всего!** 🎯