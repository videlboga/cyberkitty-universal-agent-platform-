# Формат сценариев Universal Agent Platform (KittyCore)

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
- **`steps`** (array) - Массив шагов сценария

### Опциональные поля

- **`name`** (string) - Название сценария
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

## 🏗️ Базовые типы шагов (SimpleScenarioEngine)

### `start` - Начало сценария
```json
{
  "id": "start",
  "type": "start",
  "params": {
    "message": "Начинаем сценарий"
  },
  "next_step": "welcome_message"
}
```

### `end` - Завершение сценария
```json
{
  "id": "finish",
  "type": "end",
  "params": {
    "message": "Сценарий завершен"
  }
}
```

### `action` - Выполнение действий
```json
{
  "id": "process_data",
  "type": "action",
  "params": {
    "action": "process_user_data",
    "data": "{user_input}"
  },
  "next_step": "show_result"
}
```

### `input` - Ожидание ввода пользователя
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

### `conditional_execute` - Условная логика
```json
{
  "id": "check_role",
  "type": "conditional_execute",
  "params": {
    "condition": "user_role == 'admin'",
    "true_step": "admin_menu",
    "false_step": "user_menu"
  }
}
```

**Поддерживаемые условия:**
- Сравнения: `==`, `!=`, `>`, `<`, `>=`, `<=`
- Логические операторы: `and`, `or`, `not`
- Проверка существования: `variable in context`

## 📱 Telegram Plugin (SimpleTelegramPlugin)

### `telegram_send_message` - Отправка сообщения
```json
{
  "id": "send_message",
  "type": "telegram_send_message",
  "params": {
    "chat_id": "{chat_id}",
    "text": "Привет, {user_name}!",
    "parse_mode": "HTML"
  },
  "next_step": "next_step"
}
```

**Параметры:**
- `chat_id` - ID чата (обязательно)
- `text` - Текст сообщения (обязательно)
- `parse_mode` - Режим парсинга: "HTML", "Markdown"
- `disable_web_page_preview` - Отключить превью ссылок
- `disable_notification` - Отправить без уведомления

### `telegram_send_buttons` - Отправка inline кнопок
```json
{
  "id": "send_buttons",
  "type": "telegram_send_buttons",
  "params": {
    "chat_id": "{chat_id}",
    "text": "Выберите действие:",
    "buttons": [
      [{"text": "🚀 Запустить", "callback_data": "run"}],
      [{"text": "❓ Помощь", "callback_data": "help"}]
    ]
  },
  "next_step": "handle_choice"
}
```

**Параметры:**
- `chat_id` - ID чата (обязательно)
- `text` - Текст сообщения (обязательно)
- `buttons` - Массив массивов кнопок (обязательно)

### `telegram_edit_message` - Редактирование сообщения
```json
{
  "id": "edit_message",
  "type": "telegram_edit_message",
  "params": {
    "chat_id": "{chat_id}",
    "message_id": "{message_id}",
    "text": "Обновленный текст"
  },
  "next_step": "next_step"
}
```

### `telegram_delete_message` - Удаление сообщения
```json
{
  "id": "delete_message",
  "type": "telegram_delete_message",
  "params": {
    "chat_id": "{chat_id}",
    "message_id": "{message_id}"
  },
  "next_step": "next_step"
}
```

### `telegram_send_photo` - Отправка фото
```json
{
  "id": "send_photo",
  "type": "telegram_send_photo",
  "params": {
    "chat_id": "{chat_id}",
    "photo": "https://example.com/photo.jpg",
    "caption": "Описание фото"
  },
  "next_step": "next_step"
}
```

### `telegram_send_document` - Отправка документа
```json
{
  "id": "send_document",
  "type": "telegram_send_document",
  "params": {
    "chat_id": "{chat_id}",
    "document": "path/to/file.pdf",
    "caption": "Документ"
  },
  "next_step": "next_step"
}
```

## 🗄️ MongoDB Plugin (MongoPlugin)

### `mongo_save` - Сохранение данных
```json
{
  "id": "save_user",
  "type": "mongo_save",
  "params": {
    "collection": "users",
    "document": {
      "telegram_id": "{user_id}",
      "name": "{user_name}",
      "created_at": "{current_time}"
    },
    "output_var": "save_result"
  },
  "next_step": "confirm_save"
}
```

### `mongo_get` - Получение данных
```json
{
  "id": "get_user",
  "type": "mongo_get",
  "params": {
    "collection": "users",
    "filter": {
      "telegram_id": "{user_id}"
    },
    "output_var": "user_data"
  },
  "next_step": "process_user"
}
```

### `mongo_update` - Обновление данных
```json
{
  "id": "update_user",
  "type": "mongo_update",
  "params": {
    "collection": "users",
    "filter": {
      "telegram_id": "{user_id}"
    },
    "update": {
      "$set": {
        "last_seen": "{current_time}"
      }
    },
    "output_var": "update_result"
  },
  "next_step": "next_step"
}
```

### `mongo_delete` - Удаление данных
```json
{
  "id": "delete_user",
  "type": "mongo_delete",
  "params": {
    "collection": "users",
    "filter": {
      "telegram_id": "{user_id}"
    },
    "output_var": "delete_result"
  },
  "next_step": "confirm_delete"
}
```

### `mongo_save_scenario` - Сохранение сценария
```json
{
  "id": "save_scenario",
  "type": "mongo_save_scenario",
  "params": {
    "scenario_id": "new_scenario",
    "scenario_data": {
      "scenario_id": "new_scenario",
      "name": "Новый сценарий",
      "steps": []
    },
    "output_var": "save_result"
  },
  "next_step": "confirm_save"
}
```

### `mongo_get_scenario` - Получение сценария
```json
{
  "id": "get_scenario",
  "type": "mongo_get_scenario",
  "params": {
    "scenario_id": "target_scenario",
    "output_var": "scenario_data"
  },
  "next_step": "process_scenario"
}
```

## 🧠 LLM Plugin (SimpleLLMPlugin)

### `llm_chat` - Чат с LLM
```json
{
  "id": "ask_llm",
  "type": "llm_chat",
  "params": {
    "prompt": "Объясни пользователю что такое {topic}",
    "model": "openai/gpt-4",
    "max_tokens": 150,
    "temperature": 0.7,
    "output_var": "llm_response"
  },
  "next_step": "show_response"
}
```

**Параметры:**
- `prompt` - Текст запроса (поддерживает переменные)
- `model` - Модель LLM (openai/gpt-4, anthropic/claude-3)
- `max_tokens` - Максимум токенов в ответе
- `temperature` - "Творческость" ответа (0.0-1.0)
- `output_var` - Переменная для сохранения ответа

### `llm_generate` - Генерация текста
```json
{
  "id": "generate_text",
  "type": "llm_generate",
  "params": {
    "prompt": "Напиши краткое резюме для {user_name}",
    "model": "openai/gpt-3.5-turbo",
    "output_var": "generated_text"
  },
  "next_step": "show_result"
}
```

### `llm_analyze` - Анализ текста
```json
{
  "id": "analyze_text",
  "type": "llm_analyze",
  "params": {
    "text": "{user_message}",
    "analysis_type": "sentiment",
    "output_var": "analysis_result"
  },
  "next_step": "process_analysis"
}
```

## 📚 RAG Plugin (SimpleRAGPlugin)

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

### `rag_index` - Индексация документов
```json
{
  "id": "index_document",
  "type": "rag_index",
  "params": {
    "document": "{document_text}",
    "metadata": {
      "source": "user_upload",
      "type": "manual"
    },
    "output_var": "index_result"
  },
  "next_step": "confirm_index"
}
```

## ⏰ Scheduler Plugin (SimpleSchedulerPlugin)

### `schedule_task` - Планирование задачи
```json
{
  "id": "schedule_reminder",
  "type": "schedule_task",
  "params": {
    "task_id": "reminder_{user_id}",
    "delay_seconds": 3600,
    "task_data": {
      "type": "reminder",
      "message": "Напоминание для {user_name}"
    },
    "output_var": "schedule_result"
  },
  "next_step": "confirm_schedule"
}
```

### `cancel_task` - Отмена задачи
```json
{
  "id": "cancel_reminder",
  "type": "cancel_task",
  "params": {
    "task_id": "reminder_{user_id}",
    "output_var": "cancel_result"
  },
  "next_step": "confirm_cancel"
}
```

### `list_tasks` - Список задач
```json
{
  "id": "list_user_tasks",
  "type": "list_tasks",
  "params": {
    "filter": {
      "user_id": "{user_id}"
    },
    "output_var": "tasks_list"
  },
  "next_step": "show_tasks"
}
```

## 🌐 HTTP Plugin (SimpleHTTPPlugin)

### `http_get` - GET запрос
```json
{
  "id": "get_data",
  "type": "http_get",
  "params": {
    "url": "https://api.example.com/data",
    "headers": {
      "Authorization": "Bearer {api_token}"
    },
    "params": {
      "limit": 10
    },
    "output_var": "api_data"
  },
  "next_step": "process_data"
}
```

### `http_post` - POST запрос
```json
{
  "id": "send_data",
  "type": "http_post",
  "params": {
    "url": "https://api.example.com/create",
    "json": {
      "name": "{user_name}",
      "email": "{user_email}"
    },
    "headers": {
      "Content-Type": "application/json"
    },
    "output_var": "create_result"
  },
  "next_step": "check_result"
}
```

### `http_request` - Универсальный HTTP запрос
```json
{
  "id": "api_call",
  "type": "http_request",
  "params": {
    "method": "PUT",
    "url": "https://api.example.com/update/{item_id}",
    "json": {
      "status": "updated"
    },
    "timeout": 15,
    "output_var": "update_result"
  },
  "next_step": "handle_response"
}
```

**Параметры HTTP запросов:**
- `method` - HTTP метод (GET, POST, PUT, DELETE)
- `url` - URL для запроса (поддерживает переменные)
- `headers` - HTTP заголовки
- `params` - Параметры запроса (для GET)
- `json` - JSON данные для отправки
- `data` - Данные для отправки (альтернатива json)
- `timeout` - Тайм-аут в секундах
- `output_var` - Переменная для сохранения ответа

## 🔄 Переменные и контекст

### Подстановка переменных

В параметрах шагов можно использовать переменные из контекста:

```json
{
  "text": "Привет, {user_name}! Ваш ID: {user_id}"
}
```

### Вложенные переменные

```json
{
  "text": "Ваш профиль: {user.profile.name}"
}
```

### Массивы

```json
{
  "text": "Первый элемент: {items.0}"
}
```

## 📝 Полный пример сценария

```json
{
  "scenario_id": "user_registration",
  "name": "Регистрация пользователя",
  "description": "Сценарий регистрации нового пользователя",
  "version": "1.0",
  "initial_context": {
    "registration_step": "start"
  },
  "steps": [
    {
      "id": "start",
      "type": "start",
      "params": {
        "message": "Начинаем регистрацию"
      },
      "next_step": "welcome"
    },
    {
      "id": "welcome",
      "type": "telegram_send_message",
      "params": {
        "chat_id": "{chat_id}",
        "text": "🎯 Добро пожаловать в систему!\n\nДавайте зарегистрируем вас.",
        "parse_mode": "HTML"
      },
      "next_step": "ask_name"
    },
    {
      "id": "ask_name",
      "type": "telegram_send_message",
      "params": {
        "chat_id": "{chat_id}",
        "text": "Как вас зовут?"
      },
      "next_step": "get_name"
    },
    {
      "id": "get_name",
      "type": "input",
      "params": {
        "input_type": "text",
        "output_var": "user_name"
      },
      "next_step": "save_user"
    },
    {
      "id": "save_user",
      "type": "mongo_save",
      "params": {
        "collection": "users",
        "document": {
          "telegram_id": "{user_id}",
          "name": "{user_name}",
          "registered_at": "{current_time}"
        },
        "output_var": "save_result"
      },
      "next_step": "confirm"
    },
    {
      "id": "confirm",
      "type": "telegram_send_buttons",
      "params": {
        "chat_id": "{chat_id}",
        "text": "✅ Регистрация завершена!\n\nПривет, {user_name}!",
        "buttons": [
          [{"text": "🚀 Начать работу", "callback_data": "start_work"}],
          [{"text": "❓ Помощь", "callback_data": "help"}]
        ]
      },
      "next_step": "end"
    },
    {
      "id": "end",
      "type": "end",
      "params": {
        "message": "Регистрация завершена успешно"
      }
    }
  ]
}
```

## 🚀 Лучшие практики

1. **Уникальные ID шагов** - Используйте описательные и уникальные идентификаторы
2. **Обработка ошибок** - Всегда предусматривайте альтернативные пути
3. **Переменные контекста** - Используйте понятные имена переменных
4. **Модульность** - Разбивайте сложные сценарии на простые шаги
5. **Тестирование** - Тестируйте каждый путь выполнения сценария

---

**Принцип:** ПРОСТОТА ПРЕВЫШЕ ВСЕГО! 🎯