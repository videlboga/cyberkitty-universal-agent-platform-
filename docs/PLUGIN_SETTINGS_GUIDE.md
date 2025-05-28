# 🔧 РУКОВОДСТВО ПО НАСТРОЙКЕ ПЛАГИНОВ

## 🎯 **НОВАЯ ФИЛОСОФИЯ:**

**Все настройки только в БД** - никаких переменных окружения!

### ✅ **Преимущества:**
- **Централизованное управление** - все настройки в одном месте
- **Динамическое обновление** - изменения применяются сразу
- **Graceful degradation** - плагины работают без настроек в ограниченном режиме
- **Простота развертывания** - не нужно настраивать переменные окружения
- **Безопасность** - токены хранятся в защищенной БД

---

## 🚀 **БЫСТРЫЙ СТАРТ:**

### 1. Запустите KittyCore
```bash
python app/simple_main.py
```

### 2. Проверьте статус плагинов
```bash
curl http://localhost:8000/api/v1/admin/plugins/status
```

### 3. Настройте нужные плагины через API
```bash
# Telegram
curl -X POST http://localhost:8000/api/v1/admin/plugins/telegram/settings \
  -H "Content-Type: application/json" \
  -d '{"bot_token": "YOUR_BOT_TOKEN"}'

# AmoCRM
curl -X POST http://localhost:8000/api/v1/admin/plugins/amocrm/settings \
  -H "Content-Type: application/json" \
  -d '{"base_url": "https://example.amocrm.ru", "access_token": "YOUR_TOKEN"}'

# LLM
curl -X POST http://localhost:8000/api/v1/admin/plugins/llm/settings \
  -H "Content-Type: application/json" \
  -d '{"openrouter_api_key": "sk-or-v1-YOUR-KEY"}'
```

---

## 📋 **ДОСТУПНЫЕ ПЛАГИНЫ:**

### 🤖 **Telegram Plugin**

**Endpoint:** `POST /api/v1/admin/plugins/telegram/settings`

**Параметры:**
```json
{
  "bot_token": "1234567890:ABCDEF...",  // Обязательно
  "webhook_url": "https://...",         // Опционально
  "webhook_secret": "secret"            // Опционально
}
```

**Получение настроек:** `GET /api/v1/admin/plugins/telegram/settings`

---

### 🏢 **AmoCRM Plugin**

**Endpoint:** `POST /api/v1/admin/plugins/amocrm/settings`

**Параметры:**
```json
{
  "base_url": "https://example.amocrm.ru",  // Обязательно
  "access_token": "your_access_token"       // Обязательно
}
```

**Настройка полей:** `POST /api/v1/admin/plugins/amocrm/fields`
```json
{
  "fields_map": {
    "telegram_id": {
      "id": 951775,
      "name": "TG username",
      "type": "text"
    },
    "phone": {
      "id": 881883,
      "name": "Телефон", 
      "type": "multiphonemail",
      "enums": [{"id": 881885, "value": "WORK"}]
    }
  }
}
```

**Получение настроек:** `GET /api/v1/admin/plugins/amocrm/settings`

---

### 🧠 **LLM Plugin**

**Endpoint:** `POST /api/v1/admin/plugins/llm/settings`

**Параметры:**
```json
{
  "openrouter_api_key": "sk-or-v1-...",     // Опционально
  "openai_api_key": "sk-...",               // Опционально  
  "anthropic_api_key": "sk-ant-...",        // Опционально
  "default_model": "meta-llama/llama-3.2-3b-instruct:free"
}
```

**Получение настроек:** `GET /api/v1/admin/plugins/llm/settings`

---

## 🔍 **МОНИТОРИНГ И ДИАГНОСТИКА:**

### Статус всех плагинов
```bash
GET /api/v1/admin/plugins/status
```

**Ответ:**
```json
{
  "success": true,
  "plugins": {
    "simple_telegram": {
      "name": "simple_telegram",
      "health": true,
      "settings": {
        "bot_token_set": true,
        "configured": true
      }
    }
  },
  "total_plugins": 7
}
```

### Healthcheck конкретного плагина
```bash
POST /api/v1/admin/plugins/{plugin_name}/healthcheck
```

---

## 🛠️ **РЕЖИМЫ РАБОТЫ ПЛАГИНОВ:**

### ✅ **Полнофункциональный режим**
- Все настройки заданы
- Плагин работает на 100%
- Healthcheck возвращает `true`

### ⚠️ **Ограниченный режим**
- Настройки отсутствуют или неполные
- Плагин работает с базовой функциональностью
- Четкие сообщения о том, что нужно настроить

### ❌ **Нерабочий режим**
- Критические ошибки
- Плагин не может выполнять функции
- Healthcheck возвращает `false`

---

## 📝 **ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ:**

### Python скрипт
```python
import asyncio
import httpx

async def configure_telegram():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/v1/admin/plugins/telegram/settings",
            json={"bot_token": "YOUR_TOKEN"}
        )
        print(response.json())

asyncio.run(configure_telegram())
```

### Bash скрипт
```bash
#!/bin/bash

# Настройка всех плагинов
curl -X POST http://localhost:8000/api/v1/admin/plugins/telegram/settings \
  -H "Content-Type: application/json" \
  -d '{"bot_token": "'$TELEGRAM_TOKEN'"}'

curl -X POST http://localhost:8000/api/v1/admin/plugins/amocrm/settings \
  -H "Content-Type: application/json" \
  -d '{"base_url": "'$AMO_URL'", "access_token": "'$AMO_TOKEN'"}'

# Проверка статуса
curl http://localhost:8000/api/v1/admin/plugins/status | jq
```

---

## 🔒 **БЕЗОПАСНОСТЬ:**

### Рекомендации:
1. **Используйте HTTPS** в продакшене
2. **Ограничьте доступ** к admin endpoints
3. **Регулярно ротируйте токены**
4. **Мониторьте логи** на подозрительную активность

### Логирование:
- Все операции настройки логируются
- Токены маскируются в логах как `***`
- Ошибки настройки записываются в `logs/api.log`

---

## 🚨 **УСТРАНЕНИЕ ПРОБЛЕМ:**

### Плагин не настраивается
1. Проверьте доступность MongoDB
2. Убедитесь что API запущен
3. Проверьте формат JSON в запросе

### Настройки не применяются
1. Перезапустите плагин через healthcheck
2. Проверьте логи в `logs/api.log`
3. Убедитесь что токены корректные

### MongoDB недоступен
- Плагины работают в ограниченном режиме
- Настройки не сохраняются
- Нужно восстановить подключение к БД

---

## 📚 **ДОПОЛНИТЕЛЬНЫЕ РЕСУРСЫ:**

- **API документация:** http://localhost:8000/docs
- **Пример скрипта:** `examples/configure_plugins.py`
- **Логи системы:** `logs/api.log`
- **Архитектура плагинов:** `docs/NEW_PLUGIN_GUIDE.md`

---

## 🎯 **ПРИНЦИПЫ НОВОЙ СИСТЕМЫ:**

1. **Простота превыше всего** - минимум шагов для настройки
2. **Отказоустойчивость** - система работает даже без настроек
3. **Прозрачность** - четкие сообщения о состоянии
4. **Централизация** - все настройки в одном месте
5. **Безопасность** - токены только в защищенной БД

**Настраивайте плагины легко и безопасно! 🚀** 