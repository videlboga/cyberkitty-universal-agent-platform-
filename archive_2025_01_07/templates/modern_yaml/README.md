# 🎯 LLM-Friendly YAML Шаблоны

Современные шаблоны сценариев для Universal Agent Platform.

## 📋 **ПРИНЦИПЫ АРХИТЕКТУРЫ**

### ✅ **LLM-FRIENDLY**
- YAML формат вместо JSON (лучше для ИИ)
- Правильные типы шагов (`channel_action` вместо `telegram_*`)
- Понятная структура для автоматической генерации

### ✅ **KISS (Keep It Simple, Stupid)**
- Минимум типов шагов
- Простая логика переходов
- Нет избыточной сложности

### ✅ **DRY (Don't Repeat Yourself)**
- Переиспользуемые компоненты
- Атомарные блоки
- Нет дублирования кода

### ✅ **КОНСИСТЕНТНОСТЬ**
- Единый стиль именования
- Стандартные паттерны
- Предсказуемая структура

## 🔧 **СОВРЕМЕННЫЕ ТИПЫ ШАГОВ**

### **Базовые**
```yaml
- type: start          # Начало сценария
- type: end            # Завершение сценария
- type: action         # Простое действие
- type: input          # Ожидание ввода
- type: branch         # Условные переходы
```

### **Каналы (LLM-friendly)**
```yaml
- type: channel_action # Универсальные действия с каналами
  params:
    action: send_message | send_buttons | edit_message
```

### **База данных**
```yaml
- type: mongo_insert_document
- type: mongo_find_documents  
- type: mongo_update_document
```

### **ИИ интеграция**
```yaml
- type: llm_query      # Запрос к LLM
- type: rag_search     # RAG поиск
```

## 📁 **СТРУКТУРА ШАБЛОНОВ**

```
templates/modern_yaml/
├── atomic/           # Атомарные блоки (1 функция)
├── components/       # Компоненты (2-5 шагов) 
├── scenarios/        # Полные сценарии
└── examples/         # Примеры использования
```

## 🚀 **БЫСТРЫЙ СТАРТ**

1. **Создание сценария**:
```bash
cp templates/modern_yaml/examples/basic_scenario.yaml scenarios/yaml/my_scenario.yaml
```

2. **Редактирование**:
- Измените `scenario_id`
- Настройте `initial_context`
- Адаптируйте шаги под задачу

3. **Тестирование**:
```bash
curl -X POST "http://localhost:8085/api/v1/simple/channels/test/execute" \
  -H "Content-Type: application/json" \
  -d '{"scenario_id": "my_scenario", "user_id": "test", "chat_id": "test"}'
```

## 📖 **ПРИМЕРЫ**

### **Простой чат-бот**
```yaml
scenario_id: simple_chatbot
steps:
  - id: start
    type: start
    next_step: greet
    
  - id: greet
    type: channel_action
    params:
      action: send_message
      chat_id: "{chat_id}"
      text: "Привет! Как дела?"
    next_step: wait_response
    
  - id: wait_response
    type: input
    params:
      output_var: user_message
    next_step: respond
    
  - id: respond
    type: channel_action
    params:
      action: send_message
      chat_id: "{chat_id}"
      text: "Понял: {user_message}"
    next_step: end
    
  - id: end
    type: end
```

### **Условная логика**
```yaml
scenario_id: conditional_logic
steps:
  - id: check_user_type
    type: branch
    params:
      conditions:
        - condition: "context.get('user_type') == 'admin'"
          next_step: admin_menu
        - condition: "context.get('user_type') == 'user'"
          next_step: user_menu
      default_next_step: guest_menu
```

### **LLM интеграция**
```yaml
scenario_id: ai_assistant
steps:
  - id: ask_llm
    type: llm_query
    params:
      prompt: "Пользователь спрашивает: {user_question}"
      output_var: ai_response
    next_step: send_response
    
  - id: send_response
    type: channel_action
    params:
      action: send_message
      chat_id: "{chat_id}"
      text: "{ai_response}"
    next_step: end
```

## ⚠️ **НЕ ИСПОЛЬЗУЙТЕ УСТАРЕВШИЕ ТИПЫ**

❌ **Устаревшие типы шагов:**
```yaml
# НЕ ИСПОЛЬЗУЙТЕ:
- type: telegram_send_message  # Используйте channel_action
- type: telegram_send_buttons  # Используйте channel_action
- type: telegram_edit_message  # Используйте channel_action
```

✅ **Современная замена:**
```yaml
# ИСПОЛЬЗУЙТЕ:
- type: channel_action
  params:
    action: send_message | send_buttons | edit_message
```

## 🔗 **ССЫЛКИ**

- [LLM Step Types Guide](../docs/llm_step_types_guide.md)
- [Scenario Development Guide](../docs/scenario_development_guide.md)
- [API Documentation](../docs/api_documentation.md) 