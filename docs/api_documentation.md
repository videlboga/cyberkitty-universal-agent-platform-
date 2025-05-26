# API Документация Universal Agent Platform (KittyCore)

## 🌐 Базовая информация

**Base URL**: `http://localhost:8000`  
**API Prefix**: `/simple`  
**Content-Type**: `application/json`

## 📋 Содержание

1. [Основной API](#основной-api)
2. [Служебные endpoints](#служебные-endpoints)
3. [MongoDB операции](#mongodb-операции)
4. [Выполнение шагов](#выполнение-шагов)
5. [Коды ответов](#коды-ответов)
6. [Примеры использования](#примеры-использования)

## 🚀 Основной API

### Выполнение сценария канала

Основной endpoint для выполнения сценариев.

```http
POST /simple/channels/{channel_id}/execute
Content-Type: application/json
```

**Параметры пути:**
- `channel_id` (string) - ID канала для выполнения

**Тело запроса:**
```json
{
  "user_id": "123456789",
  "chat_id": "987654321",
  "context": {
    "user_name": "Пользователь",
    "message_text": "/start",
    "custom_field": "value"
  },
  "scenario_id": "specific_scenario"
}
```

**Поля запроса:**
- `user_id` (string, optional) - ID пользователя
- `chat_id` (string, optional) - ID чата в Telegram
- `context` (object, optional) - Дополнительный контекст
- `scenario_id` (string, optional) - Конкретный сценарий для выполнения

**Ответ:**
```json
{
  "success": true,
  "scenario_id": "simple_telegram",
  "final_context": {
    "user_id": "123456789",
    "chat_id": "987654321",
    "user_name": "Пользователь",
    "execution_result": "completed"
  },
  "message": "Сценарий выполнен успешно"
}
```

**Поля ответа:**
- `success` (boolean) - Успешно ли выполнен сценарий
- `scenario_id` (string) - ID выполненного сценария
- `final_context` (object) - Финальный контекст после выполнения
- `message` (string, optional) - Сообщение о результате
- `error` (string, optional) - Ошибка, если произошла

## 🔧 Служебные endpoints

### Проверка здоровья системы

```http
GET /simple/health
```

**Ответ:**
```json
{
  "status": "healthy",
  "engine": "SimpleScenarioEngine",
  "plugins": {
    "SimpleTelegramPlugin": "healthy",
    "MongoPlugin": "healthy",
    "SimpleLLMPlugin": "healthy",
    "SimpleRAGPlugin": "healthy",
    "SimpleSchedulerPlugin": "healthy"
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### Информация о системе

```http
GET /simple/info
```

**Ответ:**
```json
{
  "engine": "SimpleScenarioEngine",
  "version": "1.0.0",
  "plugins": [
    {
      "name": "SimpleTelegramPlugin",
      "handlers": [
        "telegram_send_message",
        "telegram_send_buttons",
        "telegram_edit_message"
      ]
    },
    {
      "name": "MongoPlugin", 
      "handlers": [
        "mongo_save",
        "mongo_get",
        "mongo_update"
      ]
    }
  ],
  "total_handlers": 15
}
```

## 🗄️ MongoDB операции

### Поиск документов

```http
POST /simple/mongo/find
Content-Type: application/json
```

**Тело запроса:**
```json
{
  "collection": "users",
  "filter": {
    "telegram_id": "123456789"
  }
}
```

**Ответ:**
```json
{
  "success": true,
  "data": [
    {
      "_id": "507f1f77bcf86cd799439011",
      "telegram_id": "123456789",
      "username": "user123",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### Вставка документа

```http
POST /simple/mongo/insert
Content-Type: application/json
```

**Тело запроса:**
```json
{
  "collection": "users",
  "document": {
    "telegram_id": "987654321",
    "username": "newuser",
    "role": "user"
  }
}
```

**Ответ:**
```json
{
  "success": true,
  "data": {
    "inserted_id": "507f1f77bcf86cd799439012"
  }
}
```

### Сохранение сценария

```http
POST /simple/mongo/save-scenario
Content-Type: application/json
```

**Тело запроса:**
```json
{
  "scenario_id": "new_scenario",
  "document": {
    "scenario_id": "new_scenario",
    "name": "Новый сценарий",
    "description": "Описание сценария",
    "steps": [
      {
        "id": "start",
        "type": "start",
        "next_step": "end"
      },
      {
        "id": "end",
        "type": "end"
      }
    ]
  }
}
```

**Ответ:**
```json
{
  "success": true,
  "data": {
    "scenario_id": "new_scenario",
    "saved": true
  }
}
```

## ⚙️ Выполнение шагов

### Выполнение отдельного шага

```http
POST /simple/execute
Content-Type: application/json
```

**Тело запроса:**
```json
{
  "step": {
    "id": "send_message",
    "type": "telegram_send_message",
    "params": {
      "chat_id": "123456789",
      "text": "Привет, мир!"
    }
  },
  "context": {
    "user_id": "123456789",
    "chat_id": "123456789"
  }
}
```

**Ответ:**
```json
{
  "success": true,
  "context": {
    "user_id": "123456789",
    "chat_id": "123456789",
    "message_sent": true,
    "message_id": 42
  }
}
```

## 📊 Коды ответов

| Код | Описание |
|-----|----------|
| 200 | Успешное выполнение |
| 400 | Неверный запрос |
| 404 | Ресурс не найден |
| 500 | Внутренняя ошибка сервера |

### Примеры ошибок

**404 - Сценарий не найден:**
```json
{
  "detail": "Сценарий 'unknown_scenario' не найден в базе данных"
}
```

**500 - Ошибка выполнения:**
```json
{
  "success": false,
  "scenario_id": "failed_scenario",
  "final_context": {},
  "error": "Ошибка выполнения шага: telegram_send_message"
}
```

## 🔍 Примеры использования

### Запуск простого Telegram сценария

```bash
curl -X POST "http://localhost:8000/simple/channels/telegram_main/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "123456789",
    "chat_id": "123456789",
    "context": {
      "user_name": "Иван",
      "message_text": "/start"
    }
  }'
```

### Проверка здоровья системы

```bash
curl "http://localhost:8000/simple/health"
```

### Поиск пользователя в MongoDB

```bash
curl -X POST "http://localhost:8000/simple/mongo/find" \
  -H "Content-Type: application/json" \
  -d '{
    "collection": "users",
    "filter": {
      "telegram_id": "123456789"
    }
  }'
```

### Выполнение отдельного шага

```bash
curl -X POST "http://localhost:8000/simple/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "step": {
      "id": "test_step",
      "type": "telegram_send_message",
      "params": {
        "chat_id": "123456789",
        "text": "Тестовое сообщение"
      }
    },
    "context": {
      "user_id": "123456789"
    }
  }'
```

## 🔌 Поддерживаемые типы шагов

### Базовые типы (SimpleScenarioEngine)
- `start` - Начало сценария
- `end` - Завершение сценария
- `action` - Выполнение действий
- `input` - Ожидание ввода
- `conditional_execute` - Условная логика

### Telegram (SimpleTelegramPlugin)
- `telegram_send_message` - Отправка сообщений
- `telegram_send_buttons` - Отправка inline кнопок
- `telegram_edit_message` - Редактирование сообщений
- `telegram_delete_message` - Удаление сообщений
- `telegram_send_photo` - Отправка фото
- `telegram_send_document` - Отправка документов

### MongoDB (MongoPlugin)
- `mongo_save` - Сохранение данных
- `mongo_get` - Получение данных
- `mongo_update` - Обновление данных
- `mongo_delete` - Удаление данных
- `mongo_save_scenario` - Сохранение сценария
- `mongo_get_scenario` - Получение сценария

### LLM (SimpleLLMPlugin)
- `llm_chat` - Чат с LLM
- `llm_generate` - Генерация текста
- `llm_analyze` - Анализ текста

### RAG (SimpleRAGPlugin)
- `rag_search` - Поиск в базе знаний
- `rag_index` - Индексация документов

### Планировщик (SimpleSchedulerPlugin)
- `schedule_task` - Планирование задачи
- `cancel_task` - Отмена задачи
- `list_tasks` - Список задач

---

**Принцип:** ПРОСТОТА ПРЕВЫШЕ ВСЕГО! 🎯 