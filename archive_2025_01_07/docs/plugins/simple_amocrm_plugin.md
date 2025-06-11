# 🏢 SimpleAmoCRMPlugin

**Плагин для интеграции с AmoCRM API v4**

## 🎯 Возможности

- ✅ Поиск контактов по различным критериям (Telegram ID, телефон, email)
- ✅ Создание новых контактов с кастомными полями
- ✅ Обновление существующих контактов
- ✅ Создание сделок с привязкой к контактам
- ✅ Добавление заметок к любым сущностям
- ✅ Универсальный поиск по контактам, сделкам, компаниям
- ✅ Поддержка всех типов кастомных полей AmoCRM
- ✅ Автоматическая обработка enum значений

## ⚙️ Настройка

### Переменные окружения

```bash
# Обязательные
AMO_BASE_URL=https://your_domain.amocrm.ru
AMO_ACCESS_TOKEN=your_access_token
```

### Файл конфигурации полей (опционально)

Создайте `app/config/amo_fields.json` с картой ваших кастомных полей:

```json
{
  "telegram_id": {
    "id": 123456,
    "name": "Telegram ID",
    "type": "text",
    "code": "TELEGRAM_ID"
  },
  "phone": {
    "id": 123458,
    "name": "Телефон",
    "type": "multiphonemail",
    "code": "PHONE",
    "enums": [
      {"id": 1, "value": "WORK", "enum_code": "WORK"},
      {"id": 2, "value": "MOBILE", "enum_code": "MOBILE"}
    ]
  }
}
```

## 🔧 Типы шагов

### amocrm_find_contact

Поиск контакта по различным критериям.

```json
{
  "type": "amocrm_find_contact",
  "params": {
    "telegram_id": "123456789",
    "output_var": "found_contact"
  }
}
```

**Параметры:**
- `telegram_id` - Поиск по Telegram ID (через кастомное поле)
- `phone` - Поиск по номеру телефона
- `email` - Поиск по email адресу
- `query` - Общий поиск по запросу
- `output_var` - Переменная для сохранения результата (по умолчанию: "contact")

**Результат:**
```json
{
  "success": true,
  "contact": {...},
  "found": true
}
```

### amocrm_create_contact

Создание нового контакта.

```json
{
  "type": "amocrm_create_contact",
  "params": {
    "name": "Иван Петров",
    "first_name": "Иван",
    "last_name": "Петров",
    "custom_fields": {
      "telegram_id": "123456789",
      "phone": "+79001234567",
      "source": "Telegram"
    },
    "output_var": "new_contact"
  }
}
```

**Параметры:**
- `name` - Полное имя контакта
- `first_name` - Имя
- `last_name` - Фамилия
- `custom_fields` - Объект с кастомными полями
- `output_var` - Переменная для результата (по умолчанию: "created_contact")

### amocrm_update_contact

Обновление существующего контакта.

```json
{
  "type": "amocrm_update_contact",
  "params": {
    "contact_id": 12345,
    "update_data": {
      "phone": "+79009876543",
      "email": "new@example.com",
      "notes": "Обновленная информация"
    },
    "output_var": "updated_contact"
  }
}
```

### amocrm_create_lead

Создание новой сделки.

```json
{
  "type": "amocrm_create_lead",
  "params": {
    "name": "Важная сделка",
    "price": 150000,
    "contact_id": 12345,
    "pipeline_id": 1,
    "status_id": 142,
    "custom_fields": {
      "source": "Telegram",
      "budget": 150000
    },
    "output_var": "new_lead"
  }
}
```

### amocrm_add_note

Добавление заметки к сущности.

```json
{
  "type": "amocrm_add_note",
  "params": {
    "entity_type": "leads",
    "entity_id": 67890,
    "note_text": "Клиент проявил интерес",
    "note_type": "common",
    "output_var": "note_result"
  }
}
```

**Параметры:**
- `entity_type` - Тип сущности: "leads", "contacts", "companies"
- `entity_id` - ID сущности
- `note_text` - Текст заметки
- `note_type` - Тип заметки: "common", "call_in", "call_out" и др.

### amocrm_search

Универсальный поиск.

```json
{
  "type": "amocrm_search",
  "params": {
    "query": "Иван",
    "entity_type": "contacts",
    "limit": 10,
    "output_var": "search_results"
  }
}
```

## 🎬 Пример сценария

```json
{
  "scenario_id": "amocrm_lead_creation",
  "steps": [
    {
      "id": "find_contact",
      "type": "amocrm_find_contact",
      "params": {
        "telegram_id": "{user_telegram_id}",
        "output_var": "existing_contact"
      },
      "next_step": "check_contact"
    },
    {
      "id": "check_contact",
      "type": "conditional",
      "params": {
        "condition": "{existing_contact.found}",
        "true_step": "create_lead",
        "false_step": "create_contact"
      }
    },
    {
      "id": "create_contact",
      "type": "amocrm_create_contact",
      "params": {
        "name": "{user_name}",
        "custom_fields": {
          "telegram_id": "{user_telegram_id}",
          "source": "Telegram"
        },
        "output_var": "new_contact"
      },
      "next_step": "create_lead"
    },
    {
      "id": "create_lead",
      "type": "amocrm_create_lead",
      "params": {
        "name": "Сделка от {user_name}",
        "price": 50000,
        "contact_id": "{new_contact.contact_id || existing_contact.contact.id}",
        "output_var": "new_lead"
      },
      "next_step": "add_note"
    },
    {
      "id": "add_note",
      "type": "amocrm_add_note",
      "params": {
        "entity_type": "leads",
        "entity_id": "{new_lead.lead_id}",
        "note_text": "Сделка создана через Telegram бота"
      }
    }
  ]
}
```

## 🔍 Поддерживаемые типы полей

- **text** - Текстовые поля
- **multitext** - Многострочный текст
- **numeric** - Числовые поля
- **select** - Одиночный выбор (dropdown)
- **multiselect** - Множественный выбор
- **multiphonemail** - Телефон/Email с типом

## 🛡️ Обработка ошибок

Все ошибки сохраняются в контекст под ключом `__step_error__`:

```json
{
  "__step_error__": "AmoCRM поиск контакта: API недоступен"
}
```

## 🔧 Healthcheck

Плагин автоматически проверяет доступность AmoCRM API через endpoint `/api/v4/account`.

## 📋 Требования

- AmoCRM аккаунт с API доступом
- Access Token с правами на чтение/запись контактов и сделок
- Python пакет `httpx` для HTTP запросов

## 🎯 Использование в ЛайкПроводнике

Плагин идеально подходит для:
- Автоматического создания лидов из Telegram
- Синхронизации данных пользователей
- Добавления заметок о взаимодействиях
- Отслеживания источников трафика
- Интеграции с воронками продаж 