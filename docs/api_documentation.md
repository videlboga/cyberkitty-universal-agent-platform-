# API Документация Universal Agent Platform

## 🌐 Базовая информация

**Base URL**: `http://localhost:8000`  
**API Version**: `v1`  
**Content-Type**: `application/json`

## 📋 Содержание

1. [Аутентификация](#аутентификация)
2. [Пользователи (Users)](#пользователи-users)
3. [Агенты (Agents)](#агенты-agents)
4. [Сценарии (Scenarios)](#сценарии-scenarios)
5. [Выполнение агентов (Agent Actions)](#выполнение-агентов-agent-actions)
6. [Интеграции (Integrations)](#интеграции-integrations)
7. [Коды ответов](#коды-ответов)
8. [Примеры использования](#примеры-использования)

## 🔐 Аутентификация

В текущей версии аутентификация упрощена. В будущих версиях будет реализован JWT/OAuth2.

## 👥 Пользователи (Users)

### Получить список всех пользователей
```http
GET /api/v1/users/
```

**Ответ:**
```json
[
  {
    "id": "user_id",
    "username": "john_doe",
    "telegram_id": "123456789",
    "role": "user",
    "created_at": "2024-01-01T00:00:00Z",
    "is_active": true
  }
]
```

### Создать пользователя
```http
POST /api/v1/users/
Content-Type: application/json

{
  "username": "new_user",
  "telegram_id": "987654321",
  "role": "user"
}
```

### Получить пользователя по ID
```http
GET /api/v1/users/{user_id}
```

### Обновить пользователя
```http
PATCH /api/v1/users/{user_id}
Content-Type: application/json

{
  "username": "updated_username",
  "is_active": false
}
```

### Удалить пользователя
```http
DELETE /api/v1/users/{user_id}
```

## 🤖 Агенты (Agents)

### Получить список всех агентов
```http
GET /api/v1/agents/
```

**Ответ:**
```json
[
  {
    "id": "agent_id",
    "name": "Помощник по продажам",
    "scenario_id": "sales_scenario",
    "plugins": ["LLMPlugin", "TelegramPlugin"],
    "initial_context": {
      "greeting": "Добро пожаловать!",
      "department": "sales"
    },
    "created_at": "2024-01-01T00:00:00Z",
    "is_active": true
  }
]
```

### Создать агента
```http
POST /api/v1/agents/
Content-Type: application/json

{
  "name": "Новый агент",
  "scenario_id": "greeting_scenario",
  "plugins": ["LLMPlugin", "RAGPlugin"],
  "initial_context": {
    "role": "assistant",
    "language": "ru"
  }
}
```

**Пример ответа:**
```json
{
  "id": "507f1f77bcf86cd799439011",
  "name": "Новый агент",
  "scenario_id": "greeting_scenario",
  "plugins": ["LLMPlugin", "RAGPlugin"],
  "initial_context": {
    "role": "assistant",
    "language": "ru"
  },
  "created_at": "2024-01-01T10:30:00Z",
  "is_active": true
}
```

### Получить агента по ID
```http
GET /api/v1/agents/{agent_id}
```

### Обновить агента
```http
PATCH /api/v1/agents/{agent_id}
Content-Type: application/json

{
  "name": "Обновлённое имя",
  "plugins": ["LLMPlugin", "TelegramPlugin", "RAGPlugin"],
  "is_active": false
}
```

### Удалить агента
```http
DELETE /api/v1/agents/{agent_id}
```

## 📋 Сценарии (Scenarios)

### Получить список всех сценариев
```http
GET /api/v1/scenarios/
```

**Ответ:**
```json
[
  {
    "scenario_id": "greeting_scenario",
    "name": "Приветствие",
    "description": "Простой сценарий приветствия пользователя",
    "version": "1.0",
    "initial_context": {
      "greeting": "Привет!"
    },
    "steps": [
      {
        "id": "start",
        "type": "start",
        "params": {},
        "next_step": "greet_user"
      }
    ]
  }
]
```

### Создать сценарий
```http
POST /api/v1/scenarios/
Content-Type: application/json

{
  "scenario_id": "new_scenario",
  "name": "Новый сценарий",
  "description": "Описание нового сценария",
  "version": "1.0",
  "initial_context": {},
  "steps": [
    {
      "id": "start",
      "type": "start",
      "params": {},
      "next_step": "end"
    },
    {
      "id": "end",
      "type": "end",
      "params": {}
    }
  ]
}
```

### Получить сценарий по ID
```http
GET /api/v1/scenarios/{scenario_id}
```

### Обновить сценарий
```http
PATCH /api/v1/scenarios/{scenario_id}
Content-Type: application/json

{
  "name": "Обновлённое название",
  "description": "Новое описание"
}
```

### Удалить сценарий
```http
DELETE /api/v1/scenarios/{scenario_id}
```

---

*Продолжение следует...* 