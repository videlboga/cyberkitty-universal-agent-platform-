# 🎯 Universal Agent Platform (KittyCore)

**Универсальная платформа для создания ИИ-агентов**

**Принцип:** ПРОСТОТА ПРЕВЫШЕ ВСЕГО! 

## 🏗️ Упрощённая архитектура

```
SimpleScenarioEngine (единственный движок)
├── Базовые обработчики (start, end, action, input, conditional_execute)
└── Плагин-специфичные обработчики:
    ├── SimpleTelegramPlugin (telegram_send_message, telegram_send_buttons, telegram_edit_message)
    ├── MongoPlugin (mongo_save, mongo_get, mongo_get_scenario, mongo_save_scenario)
    ├── SimpleLLMPlugin (llm_chat, llm_generate)
    ├── SimpleRAGPlugin (rag_search, rag_index)
    ├── SimpleSchedulerPlugin (schedule_task, cancel_task)
└── SimpleHTTPPlugin (http_get, http_post, http_request)

Simple API (app/api/simple.py)
├── POST /simple/channels/{channel_id}/execute (основной endpoint)
├── GET /simple/health (проверка здоровья)
├── GET /simple/info (информация о системе)
├── POST /simple/mongo/* (MongoDB операции)
└── POST /simple/execute (выполнение отдельного шага)
```

## 🎯 Принципы архитектуры

1. ✅ **Один движок** - `SimpleScenarioEngine` вместо множества
2. ✅ **Простая система плагинов** - все наследуют `BasePlugin`
3. ✅ **Минимум API endpoints** - основной функционал через один endpoint
4. ✅ **Минимум зависимостей** - только необходимые библиотеки
5. ✅ **Явная передача контекста** - контекст передается между компонентами
6. ✅ **Разделение ответственности** - движок универсален, плагины специализированы

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

# Логирование
LOG_LEVEL=INFO

# API конфигурация
HOST=0.0.0.0
PORT=8000
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

**POST /simple/channels/{channel_id}/execute**

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

- **GET /simple/health** - Проверка здоровья системы
- **GET /simple/info** - Информация о системе и плагинах
- **POST /simple/execute** - Выполнение отдельного шага
- **POST /simple/mongo/find** - Поиск в MongoDB
- **POST /simple/mongo/insert** - Вставка в MongoDB
- **POST /simple/mongo/save-scenario** - Сохранение сценария

## 🎬 Типы шагов сценариев

### Базовые (в SimpleScenarioEngine):
- `start` - Начало сценария
- `end` - Завершение сценария  
- `action` - Выполнение действий
- `input` - Ожидание ввода пользователя
- `conditional_execute` - Условная логика

### Telegram (SimpleTelegramPlugin):
- `telegram_send_message` - Отправка сообщений
- `telegram_send_buttons` - Отправка inline кнопок
- `telegram_edit_message` - Редактирование сообщений
- `telegram_delete_message` - Удаление сообщений
- `telegram_send_photo` - Отправка фото
- `telegram_send_document` - Отправка документов

### MongoDB (MongoPlugin):
- `mongo_save` - Сохранение данных
- `mongo_get` - Получение данных
- `mongo_update` - Обновление данных
- `mongo_delete` - Удаление данных
- `mongo_save_scenario` - Сохранение сценария
- `mongo_get_scenario` - Получение сценария

### LLM (SimpleLLMPlugin):
- `llm_chat` - Чат с LLM
- `llm_generate` - Генерация текста
- `llm_analyze` - Анализ текста

### RAG (SimpleRAGPlugin):
- `rag_search` - Поиск в базе знаний
- `rag_index` - Индексация документов

### Планировщик (SimpleSchedulerPlugin):
- `schedule_task` - Планирование задачи
- `cancel_task` - Отмена задачи
- `list_tasks` - Список задач

### HTTP клиент (SimpleHTTPPlugin):
- `http_get` - GET запрос к внешнему API
- `http_post` - POST запрос с данными
- `http_put` - PUT запрос для обновления
- `http_delete` - DELETE запрос
- `http_request` - Универсальный HTTP запрос

## 📝 Пример сценария

```json
{
  "scenario_id": "simple_demo",
  "description": "Демонстрационный сценарий",
  "initial_context": {
    "demo_mode": true
  },
  "steps": [
    {
      "id": "start",
      "type": "start",
      "params": {
        "message": "Начинаем демо-сценарий"
      },
      "next_step": "welcome"
    },
    {
      "id": "welcome", 
      "type": "telegram_send_message",
      "params": {
        "chat_id": "{chat_id}",
        "text": "Привет, {user_name}! Это демо-сценарий.",
        "parse_mode": "HTML"
      },
      "next_step": "check_role"
    },
    {
      "id": "check_role",
      "type": "conditional_execute",
      "params": {
        "condition": "user_role == 'admin'",
        "true_step": "admin_menu",
        "false_step": "user_menu"
      }
    },
    {
      "id": "user_menu",
      "type": "telegram_send_buttons",
      "params": {
        "chat_id": "{chat_id}",
        "text": "Выберите действие:",
        "buttons": [
          [{"text": "🚀 Запустить", "callback_data": "run"}],
          [{"text": "❓ Помощь", "callback_data": "help"}]
        ]
      },
      "next_step": "end"
    },
    {
      "id": "end",
      "type": "end",
      "params": {
        "message": "Сценарий завершен"
      }
    }
  ]
}
```

## 🧪 Тестирование

```bash
# Запуск всех тестов
pytest tests/

# Тест конкретного компонента
pytest tests/test_simple_engine.py

# Проверка здоровья системы
curl http://localhost:8000/simple/health

# Информация о системе
curl http://localhost:8000/simple/info
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
docker run -p 8000:8000 kittycore
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