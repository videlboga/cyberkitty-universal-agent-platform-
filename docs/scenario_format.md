# Формат сценариев Universal Agent Platform

## 📋 Структура сценария

Каждый сценарий представляет собой JSON-файл со следующей структурой:

```json
{
  "scenario_id": "unique_scenario_id",
  "name": "Человекочитаемое название",
  "description": "Описание назначения сценария",
  "version": "1.0",
  "initial_context": {
    "variable1": "value1",
    "variable2": "value2"
  },
  "steps": [
    {
      "id": "step_1",
      "type": "step_type",
      "params": {
        "param1": "value1"
      },
      "next_step": "step_2"
    }
  ]
}
```

### Обязательные поля

- **`scenario_id`** (string) - Уникальный идентификатор сценария
- **`name`** (string) - Название сценария
- **`steps`** (array) - Массив шагов сценария

### Опциональные поля

- **`description`** (string) - Описание сценария
- **`version`** (string) - Версия сценария
- **`initial_context`** (object) - Начальный контекст

## 🔧 Структура шага

```json
{
  "id": "unique_step_id",
  "type": "step_type",
  "params": {
    "parameter": "value"
  },
  "next_step": "next_step_id"
}
```

### Поля шага

- **`id`** (string, обязательное) - Уникальный ID шага
- **`type`** (string, обязательное) - Тип шага
- **`params`** (object) - Параметры шага
- **`next_step`** (string) - ID следующего шага

## 🏗️ Базовые типы шагов

### `start` - Начало сценария
```json
{
  "id": "start",
  "type": "start",
  "params": {},
  "next_step": "welcome_message"
}
```

### `end` - Завершение сценария
```json
{
  "id": "finish",
  "type": "end",
  "params": {}
}
```

### `message` - Отправка сообщения
```json
{
  "id": "welcome",
  "type": "message",
  "params": {
    "text": "Привет, {user_name}!"
  },
  "next_step": "ask_question"
}
```

### `input` - Запрос ввода
```json
{
  "id": "get_name",
  "type": "input",
  "params": {
    "prompt": "Как вас зовут?",
    "input_type": "text",
    "output_var": "user_name"
  },
  "next_step": "greet_user"
}
```

**Типы ввода:**
- `text` - Текстовый ввод
- `callback_query` - Callback от inline-кнопок

### `branch` - Условное ветвление
```json
{
  "id": "check_age",
  "type": "branch",
  "params": {
    "conditions": [
      {
        "condition": "context.user_age >= 18",
        "next_step": "adult_content"
      }
    ],
    "default_next_step": "minor_content"
  }
}
```

### `log` - Логирование
```json
{
  "id": "log_action",
  "type": "log",
  "params": {
    "message": "User {user_name} started scenario",
    "level": "INFO"
  },
  "next_step": "next_step"
}
```

## 🧠 LLM Plugin - Шаги языковых моделей

### `llm_request` - Запрос к LLM
```json
{
  "id": "ask_llm",
  "type": "llm_request",
  "params": {
    "prompt": "Объясни пользователю что такое {topic}",
    "model": "deepseek/deepseek-chat",
    "max_tokens": 150,
    "temperature": 0.7,
    "output_var": "llm_response"
  },
  "next_step": "show_response"
}
```

**Параметры:**
- `prompt` - Текст запроса (поддерживает переменные из контекста)
- `model` - Модель LLM (по умолчанию: deepseek/deepseek-chat)
- `max_tokens` - Максимум токенов в ответе
- `temperature` - "Творческость" ответа (0.0-1.0)
- `output_var` - Переменная для сохранения ответа

## 📚 RAG Plugin - Семантический поиск

### `rag_search` - Поиск в базе знаний
```json
{
  "id": "search_docs",
  "type": "rag_search",
  "params": {
    "query": "Как настроить {feature_name}",
    "top_k": 3,
    "output_var": "search_results"
  },
  "next_step": "process_results"
}
```

**Параметры:**
- `query` - Поисковый запрос
- `top_k` - Количество результатов (по умолчанию: 3)
- `output_var` - Переменная для сохранения результатов

## 📱 Telegram Plugin - Мессенджер

### `telegram_send_message` - Отправка сообщения
```json
{
  "id": "send_telegram",
  "type": "telegram_send_message",
  "params": {
    "chat_id": "{chat_id}",
    "text": "Ваш результат: {result}",
    "reply_markup": {
      "inline_keyboard": [
        [
          {
            "text": "Да ✅",
            "callback_data": "answer_yes"
          },
          {
            "text": "Нет ❌", 
            "callback_data": "answer_no"
          }
        ]
      ]
    },
    "output_var": "message_info"
  },
  "next_step": "wait_callback"
}
```

### `telegram_edit_message` - Редактирование сообщения
```json
{
  "id": "edit_telegram",
  "type": "telegram_edit_message",
  "params": {
    "chat_id": "{chat_id}",
    "message_id": "{message_id}",
    "text": "Обновлённый текст",
    "reply_markup": null
  },
  "next_step": "next_step"
}
```

## 🗄️ MongoDB Plugin - База данных

### `mongo_insert_one` - Вставка документа
```json
{
  "id": "save_user",
  "type": "mongo_insert_one",
  "params": {
    "collection": "users",
    "document": {
      "name": "{user_name}",
      "created_at": "{current_timestamp}"
    },
    "output_var": "insert_result"
  },
  "next_step": "confirm_save"
}
```

### `mongo_find_one` - Поиск документа
```json
{
  "id": "find_user",
  "type": "mongo_find_one",
  "params": {
    "collection": "users",
    "filter": {
      "telegram_id": "{telegram_id}"
    },
    "output_var": "user_data"
  },
  "next_step": "process_user"
}
```

### `mongo_update_one` - Обновление документа
```json
{
  "id": "update_user",
  "type": "mongo_update_one",
  "params": {
    "collection": "users",
    "filter": {
      "telegram_id": "{telegram_id}"
    },
    "update": {
      "$set": {
        "last_seen": "{current_timestamp}",
        "status": "active"
      }
    },
    "output_var": "update_result"
  },
  "next_step": "confirm_update"
}
```

### `mongo_delete_one` - Удаление документа
```json
{
  "id": "delete_user",
  "type": "mongo_delete_one",
  "params": {
    "collection": "users",
    "filter": {
      "telegram_id": "{telegram_id}"
    },
    "output_var": "delete_result"
  },
  "next_step": "confirm_delete"
}
```

## 🔄 Работа с контекстом

### Переменные из контекста
Используйте фигурные скобки для подстановки переменных:
```json
{
  "text": "Привет, {user_name}! Сегодня {current_date}"
}
```

### Сохранение результатов
Используйте `output_var` для сохранения результатов шагов:
```json
{
  "params": {
    "output_var": "variable_name"
  }
}
```

### Доступ к результатам
После сохранения, переменные доступны в последующих шагах:
```json
{
  "text": "LLM ответил: {llm_response}"
}
```

## ✅ Пример полного сценария

```json
{
  "scenario_id": "user_registration",
  "name": "Регистрация пользователя",
  "description": "Сценарий для регистрации нового пользователя",
  "version": "1.0",
  "initial_context": {
    "greeting": "Добро пожаловать!"
  },
  "steps": [
    {
      "id": "start",
      "type": "start",
      "params": {},
      "next_step": "welcome"
    },
    {
      "id": "welcome",
      "type": "message",
      "params": {
        "text": "{greeting} Давайте зарегистрируем вас в системе."
      },
      "next_step": "get_name"
    },
    {
      "id": "get_name",
      "type": "input",
      "params": {
        "prompt": "Как вас зовут?",
        "output_var": "user_name"
      },
      "next_step": "save_user"
    },
    {
      "id": "save_user",
      "type": "mongo_insert_one",
      "params": {
        "collection": "users",
        "document": {
          "name": "{user_name}",
          "registered_at": "{current_timestamp}"
        },
        "output_var": "save_result"
      },
      "next_step": "confirm"
    },
    {
      "id": "confirm",
      "type": "message",
      "params": {
        "text": "Спасибо, {user_name}! Вы успешно зарегистрированы."
      },
      "next_step": "end"
    },
    {
      "id": "end",
      "type": "end",
      "params": {}
    }
  ]
} 