# LLM-Friendly Справка: Типы Шагов для Universal Agent Platform

## 🎯 ОСНОВНЫЕ ПРИНЦИПЫ
- **Простота превыше всего** - используй минимум типов шагов
- **ChannelManager** отвечает за все Telegram операции  
- **НЕ используй** `telegram_send_message` - используй `channel_action`
- **YAML превыше JSON** - лучше для ИИ генерации
- **Контекст** передается явно между шагами

## 📋 ПРАВИЛЬНЫЕ ТИПЫ ШАГОВ

### Базовые операции
```yaml
# Начало сценария
- id: start
  type: start
  next_step: next_step_id

# Завершение сценария  
- id: end
  type: end

# Простое действие
- id: do_something
  type: action
  params:
    message: "Действие выполнено"
  next_step: next_step_id

# Ожидание ввода пользователя
- id: wait_user
  type: input
  params:
    prompt: "Введите ответ:"
    output_var: user_input
  next_step: process_input

# Условные переходы
- id: check_condition
  type: branch
  params:
    conditions:
      - condition: "context.get('user_type') == 'admin'"
        next_step: admin_panel
      - condition: "context.get('user_type') == 'user'"
        next_step: user_panel
    default_next_step: guest_panel
```

### Работа с каналами (LLM-friendly)
```yaml
# ✅ ПРАВИЛЬНО - отправка сообщения
- id: send_message
  type: channel_action
  params:
    action: send_message
    chat_id: "{chat_id}"
    text: "Привет! Как дела?"
    parse_mode: HTML
  next_step: wait_response

# ✅ ПРАВИЛЬНО - отправка кнопок
- id: send_menu
  type: channel_action
  params:
    action: send_buttons
    chat_id: "{chat_id}"
    text: "Выберите действие:"
    buttons:
      - - text: "📊 Статистика"
          callback_data: "stats"
      - - text: "⚙️ Настройки"
          callback_data: "settings"
  next_step: wait_callback

# ✅ ПРАВИЛЬНО - редактирование сообщения
- id: edit_message
  type: channel_action
  params:
    action: edit_message
    chat_id: "{chat_id}"
    message_id: "{message_id}"
    text: "Обновленный текст"
  next_step: next_step
```

### MongoDB операции
```yaml
# Поиск документов
- id: find_users
  type: mongo_find_documents
  params:
    collection: "users"
    filter: {"active": true}
    output_var: active_users
  next_step: process_users

# Вставка документа
- id: save_user
  type: mongo_insert_document
  params:
    collection: "users"
    document:
      name: "{user_name}"
      created_at: "{current_timestamp}"
    output_var: insert_result
  next_step: confirm_save

# Обновление документа
- id: update_user
  type: mongo_update_document
  params:
    collection: "users"
    filter: {"user_id": "{user_id}"}
    update:
      "$set":
        last_active: "{current_timestamp}"
        status: "online"
    output_var: update_result
  next_step: next_step
```

### LLM интеграция
```yaml
# Запрос к LLM
- id: ask_ai
  type: llm_query
  params:
    prompt: |
      Пользователь спрашивает: {user_question}
      
      Ответь кратко и по делу.
    model: "gpt-4"
    output_var: ai_response
  next_step: send_ai_response

# Чат с LLM (с историей)
- id: chat_with_ai
  type: llm_chat
  params:
    message: "{user_message}"
    system_prompt: "Ты полезный ассистент."
    output_var: chat_response
  next_step: send_chat_response
```

### RAG (поиск знаний)
```yaml
# Поиск в базе знаний
- id: search_knowledge
  type: rag_search
  params:
    query: "{user_question}"
    collection: "knowledge_base"
    limit: 5
    output_var: search_results
  next_step: generate_answer

# Генерация ответа на основе RAG
- id: generate_rag_answer
  type: rag_answer
  params:
    question: "{user_question}"
    context: "{search_results}"
    output_var: rag_answer
  next_step: send_rag_answer
```

### Переключение сценариев
```yaml
# Переход к другому сценарию
- id: switch_to_registration
  type: switch_scenario
  params:
    target_scenario: "user_registration"
    preserve_context: true
    context_updates:
      previous_scenario: "main_menu"
      switch_reason: "new_user"
  next_step: end
```

## ❌ УСТАРЕВШИЕ ТИПЫ ШАГОВ (НЕ ИСПОЛЬЗУЙТЕ!)

```yaml
# ❌ УСТАРЕЛО - НЕ ИСПОЛЬЗУЙТЕ
- type: telegram_send_message
- type: telegram_edit_message
- type: telegram_send_buttons
- type: telegram_start_polling
- type: telegram_update_token
- type: telegram_load_token
```

## ✅ СОВРЕМЕННЫЕ ЗАМЕНЫ

| ❌ Устарело | ✅ Используйте вместо |
|-------------|----------------------|
| `telegram_send_message` | `channel_action` с `action: send_message` |
| `telegram_send_buttons` | `channel_action` с `action: send_buttons` |
| `telegram_edit_message` | `channel_action` с `action: edit_message` |

## 🎯 ПОЛНЫЙ ПРИМЕР СОВРЕМЕННОГО СЦЕНАРИЯ

```yaml
scenario_id: modern_example
description: "Современный LLM-friendly сценарий"

initial_context:
  version: "2.0"
  architecture: "modern"

steps:
  # Начало
  - id: start
    type: start
    next_step: greet_user

  # Приветствие
  - id: greet_user
    type: channel_action
    params:
      action: send_message
      chat_id: "{chat_id}"
      text: |
        👋 **Добро пожаловать!**
        
        Как вас зовут?
      parse_mode: HTML
    next_step: wait_name

  # Ожидание имени
  - id: wait_name
    type: input
    params:
      prompt: "Введите ваше имя:"
      output_var: user_name
    next_step: save_user

  # Сохранение пользователя
  - id: save_user
    type: mongo_insert_document
    params:
      collection: "users"
      document:
        name: "{user_name}"
        chat_id: "{chat_id}"
        registered_at: "{current_timestamp}"
    next_step: ask_llm

  # Запрос к ИИ
  - id: ask_llm
    type: llm_query
    params:
      prompt: "Пользователь {user_name} зарегистрировался. Поприветствуй его."
      output_var: ai_greeting
    next_step: send_ai_greeting

  # Отправка ИИ приветствия
  - id: send_ai_greeting
    type: channel_action
    params:
      action: send_message
      chat_id: "{chat_id}"
      text: "{ai_greeting}"
    next_step: main_menu

  # Главное меню
  - id: main_menu
    type: channel_action
    params:
      action: send_buttons
      chat_id: "{chat_id}"
      text: "Что хотите сделать?"
      buttons:
        - - text: "💬 Чат с ИИ"
            callback_data: "ai_chat"
        - - text: "📚 Поиск знаний"
            callback_data: "knowledge_search"
        - - text: "✅ Завершить"
            callback_data: "finish"
    next_step: end

  # Завершение
  - id: end
    type: end
```

## 🔗 ПОЛЕЗНЫЕ ССЫЛКИ

- [Базовый шаблон](../templates/modern_yaml/examples/basic_scenario.yaml)
- [Современные шаблоны](../templates/modern_yaml/README.md)
- [API документация](api_documentation.md) 