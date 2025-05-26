# 🧩 Атомарные сценарии KittyCore

Коллекция атомарных (неделимых) сценариев для построения сложных пользовательских процессов.

## 🎯 Принцип атомарности

**Один атомарный сценарий = одна конкретная задача**

- ✅ Отправить сообщение в Telegram
- ✅ Сохранить данные в MongoDB  
- ✅ Запросить ответ у LLM
- ❌ "Зарегистрировать пользователя и отправить приветствие" (это уже композитный сценарий)

## 📋 Доступные атомарные сценарии

| # | Сценарий | Описание | Плагины | Сложность |
|---|----------|----------|---------|-----------|
| 01 | `telegram_send_message` | Отправка простого сообщения | SimpleTelegramPlugin | 🟢 |
| 02 | `telegram_send_buttons` | Отправка сообщения с кнопками | SimpleTelegramPlugin | 🟢 |
| 03 | `llm_query` | Запрос к языковой модели | SimpleLLMPlugin | 🟡 |
| 04 | `mongo_save_data` | Сохранение данных в MongoDB | MongoPlugin | 🟢 |
| 05 | `mongo_find_data` | Поиск данных в MongoDB | MongoPlugin | 🟢 |
| 06 | `rag_search` | Семантический поиск в базе знаний | SimpleRAGPlugin | 🟡 |
| 07 | `conditional_branch` | Условное ветвление | Core Engine | 🟡 |
| 08 | `switch_scenario` | Переключение сценариев | Core Engine | 🟡 |
| 09 | `scheduler_create_task` | Создание отложенной задачи | SimpleSchedulerPlugin | 🟡 |
| 10 | `log_message` | Логирование сообщений | Core Engine | 🟢 |

## 🚀 Быстрый старт

### 1. Использование атомарного сценария

```bash
# Выполнить атомарный сценарий напрямую
curl -X POST http://localhost:8000/simple/execute \
  -H "Content-Type: application/json" \
  -d '{
    "scenario_id": "atomic_telegram_send_message",
    "context": {
      "chat_id": "123456789",
      "text": "Привет из атомарного сценария!"
    }
  }'
```

### 2. Композиция атомарных сценариев

```json
{
  "scenario_id": "user_welcome_composite",
  "steps": [
    {
      "id": "start",
      "type": "start",
      "next_step": "log_start"
    },
    {
      "id": "log_start", 
      "type": "switch_scenario",
      "params": {
        "target_scenario": "atomic_log_message",
        "context_updates": {
          "message": "Начинаем приветствие пользователя {user_name}",
          "level": "INFO"
        }
      },
      "next_step": "send_welcome"
    },
    {
      "id": "send_welcome",
      "type": "switch_scenario", 
      "params": {
        "target_scenario": "atomic_telegram_send_message",
        "context_updates": {
          "text": "Добро пожаловать, {user_name}!"
        }
      },
      "next_step": "save_user"
    },
    {
      "id": "save_user",
      "type": "switch_scenario",
      "params": {
        "target_scenario": "atomic_mongo_save_data",
        "context_updates": {
          "collection": "users",
          "document": {
            "user_id": "{user_id}",
            "name": "{user_name}",
            "welcomed_at": "{current_time}"
          }
        }
      },
      "next_step": "end"
    },
    {
      "id": "end",
      "type": "end"
    }
  ]
}
```

## 🔧 Структура атомарного сценария

```json
{
  "atomic_template": "имя_шаблона",
  "version": "1.0",
  "description": "Краткое описание",
  "author": "KittyCore Universal Agent Platform",
  
  "parameters": {
    "param_name": {
      "type": "string|number|boolean|object|array",
      "description": "Описание параметра",
      "required": true|false,
      "default": "значение_по_умолчанию",
      "example": "пример_значения"
    }
  },
  
  "scenario_id": "atomic_имя_шаблона",
  "steps": [
    {
      "id": "start",
      "type": "start",
      "next_step": "main_action"
    },
    {
      "id": "main_action", 
      "type": "тип_шага",
      "params": {
        "param1": "{param1}",
        "param2": "{param2}"
      },
      "next_step": "end"
    },
    {
      "id": "end",
      "type": "end"
    }
  ],
  
  "examples": [...],
  "requirements": {...},
  "output": {...}
}
```

## 💡 Примеры композиции

### Простая цепочка
```
atomic_log_message → atomic_telegram_send_message → atomic_mongo_save_data
```

### Условное ветвление
```
atomic_mongo_find_data → atomic_conditional_branch
                      ├─ (если найден) → atomic_telegram_send_message
                      └─ (если не найден) → atomic_switch_scenario
```

### LLM + RAG цепочка
```
atomic_rag_search → atomic_llm_query → atomic_telegram_send_message
```

## 🎨 Лучшие практики

### ✅ Хорошие атомарные сценарии
- **Одна ответственность**: делают только одну вещь
- **Переиспользуемые**: можно использовать в разных контекстах
- **Параметризованные**: настраиваются через контекст
- **Предсказуемые**: всегда возвращают ожидаемый результат

### ❌ Плохие атомарные сценарии
- Делают несколько несвязанных действий
- Жестко привязаны к конкретному случаю использования
- Имеют побочные эффекты
- Зависят от глобального состояния

### 🔄 Композиция сценариев

1. **Последовательная**: A → B → C
2. **Условная**: A → (условие) → B или C
3. **Параллельная**: A → [B, C, D] → E
4. **Циклическая**: A → B → (условие) → A или C

## 🧪 Тестирование

### Тест атомарного сценария
```bash
# Тест отправки сообщения
curl -X POST http://localhost:8000/simple/execute \
  -H "Content-Type: application/json" \
  -d '{
    "scenario_id": "atomic_telegram_send_message",
    "context": {
      "chat_id": "123456789",
      "text": "Тестовое сообщение"
    }
  }'
```

### Тест композитного сценария
```bash
# Тест цепочки: лог → сообщение → сохранение
curl -X POST http://localhost:8000/simple/execute \
  -H "Content-Type: application/json" \
  -d '{
    "scenario_id": "test_composite",
    "context": {
      "user_id": "test_user",
      "chat_id": "123456789",
      "user_name": "Тестовый пользователь"
    }
  }'
```

## 📊 Мониторинг

Все атомарные сценарии автоматически логируют:
- ✅ Успешное выполнение
- ❌ Ошибки и исключения
- ⏱️ Время выполнения
- 📝 Входные и выходные данные

Логи доступны в:
```
logs/engine.log     - Выполнение сценариев
logs/plugins.log    - Работа плагинов
logs/errors.log     - Ошибки системы
```

## 🔗 Связанные компоненты

### Плагины
- `SimpleTelegramPlugin` - Telegram интеграция
- `SimpleLLMPlugin` - Языковые модели
- `SimpleRAGPlugin` - Семантический поиск
- `MongoPlugin` - База данных
- `SimpleSchedulerPlugin` - Планировщик задач

### API Endpoints
- `POST /simple/execute` - Выполнение сценария
- `GET /simple/health` - Проверка здоровья
- `GET /simple/info` - Информация о системе

## 🛠️ Создание нового атомарного сценария

1. **Скопируйте шаблон**:
```bash
cp templates/atomic/01_telegram_send_message.json templates/atomic/11_my_atomic.json
```

2. **Измените метаданные**:
```json
{
  "atomic_template": "my_atomic_action",
  "description": "Описание вашего действия"
}
```

3. **Определите параметры**:
```json
{
  "parameters": {
    "my_param": {
      "type": "string",
      "description": "Мой параметр",
      "required": true
    }
  }
}
```

4. **Настройте шаги**:
```json
{
  "steps": [
    {
      "id": "main_action",
      "type": "my_step_type",
      "params": {
        "param": "{my_param}"
      }
    }
  ]
}
```

5. **Добавьте примеры и тесты**

## 🤝 Вклад в развитие

Для добавления новых атомарных сценариев:
1. Создайте файл в `templates/atomic/`
2. Следуйте принципу атомарности
3. Добавьте примеры и документацию
4. Протестируйте сценарий
5. Обновите этот README
6. Создайте pull request

---

**💡 Помните**: Атомарные сценарии - это строительные блоки. Их сила в простоте и переиспользуемости!

📧 **Поддержка**: [GitHub Issues](https://github.com/yourusername/kittycore/issues)  
📖 **Документация**: [docs/scenario_format.md](../../docs/scenario_format.md) 