# 🔧 Руководство по настройке AmoCRM плагина

Это руководство поможет вам настроить AmoCRM плагин через API и решить проблемы с шаблонами.

## 📋 Обзор проблем

### ❌ Проблемы ДО исправления:
1. **AmoCRM healthcheck: отсутствуют настройки** - плагин не может найти настройки в MongoDB
2. **Простые шаблоны** - поддержка только `{variable}`, нет `{{user}}`, `{user.name}`, `{items[0]}`
3. **Permission denied** - проблемы с правами доступа к логам

### ✅ Решения ПОСЛЕ исправления:
1. **Автоматическая настройка** через API эндпоинт `/api/v1/simple/amocrm/setup`
2. **Продвинутые шаблоны** с поддержкой всех современных форматов
3. **Исправлены права доступа** через docker-compose.yml

## 🚀 Быстрый старт

### 1. Проверка статуса AmoCRM

```bash
curl -X GET "http://localhost:8085/api/v1/simple/amocrm/status"
```

**Ответ:**
```json
{
  "success": true,
  "plugin_registered": true,
  "has_settings": false,
  "healthcheck_passed": false,
  "has_field_mapping": false,
  "ready_for_use": false,
  "recommendations": [
    "Настройте AmoCRM через /api/v1/simple/amocrm/setup"
  ]
}
```

### 2. Настройка AmoCRM плагина

```bash
curl -X POST "http://localhost:8085/api/v1/simple/amocrm/setup" \
  -H "Content-Type: application/json" \
  -d '{
    "domain": "your-account.amocrm.ru",
    "client_id": "your_client_id",
    "client_secret": "your_client_secret", 
    "redirect_uri": "https://your-app.com/oauth/callback",
    "access_token": "your_access_token",
    "refresh_token": "your_refresh_token"
  }'
```

**Успешный ответ:**
```json
{
  "success": true,
  "message": "AmoCRM плагин успешно настроен",
  "details": {
    "domain": "your-account.amocrm.ru",
    "healthcheck_passed": true,
    "field_mapping_loaded": 3,
    "entities_mapped": ["contacts", "leads", "companies"],
    "total_fields": 45
  }
}
```

### 3. Проверка после настройки

```bash
curl -X GET "http://localhost:8085/api/v1/simple/amocrm/status"
```

**Ответ после настройки:**
```json
{
  "success": true,
  "plugin_registered": true,
  "has_settings": true,
  "healthcheck_passed": true,
  "has_field_mapping": true,
  "ready_for_use": true,
  "domain": "your-account.amocrm.ru",
  "field_stats": {
    "contacts": 15,
    "leads": 12,
    "companies": 8
  },
  "recommendations": []
}
```

## 🧪 Тестирование шаблонов

### Запуск тестов
```bash
cd /path/to/kittycore
python scripts/test_templates.py
```

### Поддерживаемые форматы шаблонов

#### 1. Простые переменные
```yaml
text: "Привет, {name}! Твой ID: {user_id}"
# Результат: "Привет, Андрей! Твой ID: 12345"
```

#### 2. Django/Jinja2 стиль
```yaml
text: "Пользователь {{name}} возраст {{age}}"
# Результат: "Пользователь Андрей возраст 25"
```

#### 3. Вложенные объекты
```yaml
text: "Email: {user.email}, город: {user.profile.city}"
# Результат: "Email: ivan@example.com, город: Москва"
```

#### 4. Элементы массивов
```yaml
text: "Первый товар: {items[0].name} за {items[0].price} руб"
# Результат: "Первый товар: Laptop за 50000 руб"
```

#### 5. Специальные переменные
```yaml
text: "Сообщение от {current_datetime}"
# Результат: "Сообщение от 2024-05-29 10:30:45"
```

#### 6. Комбинированные
```yaml
text: "{{user.name}} из {{user.profile.city}} заказал {items[0].name} в {current_time}"
# Результат: "Иван из Москва заказал Laptop в 10:30:45"
```

### Пример использования в сценарии

```yaml
scenario_id: "modern_template_demo"
steps:
  - id: send_welcome
    type: channel_action
    params:
      action: send_message
      chat_id: "{telegram_data.chat_id}"
      text: |
        🌟 Привет, {{user.name}}!
        
        📊 Твоя информация:
        • ID: {user_id}
        • Email: {user.profile.email}
        • Город: {{user.profile.city}}
        
        🛒 Последний заказ:
        • Товар: {orders[0].item.name}
        • Цена: {{orders[0].price}} руб
        
        ⏰ Время: {current_datetime}
      parse_mode: "HTML"
```

## 🔧 Устранение проблем

### Проблема: Permission denied для логов

**Решение:** Обновлен `docker-compose.yml` с правильными правами:
```yaml
volumes:
  - ./logs:/app/logs:rw  # Права на запись
```

### Проблема: AmoCRM плагин не инициализируется

**Решение:** Используйте API для настройки:
1. `GET /api/v1/simple/amocrm/status` - проверка статуса
2. `POST /api/v1/simple/amocrm/setup` - автоматическая настройка

### Проблема: Шаблоны не работают

**Решение:** Обновлен `TemplateResolver` с поддержкой:
- `{variable}` - простые переменные
- `{{variable}}` - Django стиль  
- `{user.name}` - вложенные объекты
- `{items[0]}` - массивы
- `{current_timestamp}` - специальные переменные

## 📚 API Endpoints

### AmoCRM управление
- `GET /api/v1/simple/amocrm/status` - статус плагина
- `POST /api/v1/simple/amocrm/setup` - настройка плагина

### Общие endpoints  
- `GET /health` - проверка здоровья системы
- `POST /api/v1/simple/execute` - выполнение шагов
- `POST /api/v1/simple/channels/{channel_id}/execute` - выполнение сценариев

## 🎯 Что было исправлено

### ✅ Template Resolution (ГОТОВО)
- Создан мощный `TemplateResolver` класс
- Поддержка всех современных форматов шаблонов
- Интеграция с `SimpleScenarioEngine`
- Тестовый скрипт для проверки

### ✅ AmoCRM Plugin Configuration (ГОТОВО)  
- API endpoint для автоматической настройки
- Динамическая загрузка настроек из MongoDB
- Автоматическая загрузка карты полей
- Проверка состояния через healthcheck

### ✅ Docker & Permissions (ГОТОВО)
- Исправлены права доступа к папке logs
- Синхронизированы порты в docker-compose
- Добавлены volumes для сценариев и логов

## 🚀 Следующие шаги

1. **Перезапустите контейнеры:**
   ```bash
   docker-compose down && docker-compose up -d
   ```

2. **Настройте AmoCRM:**
   ```bash
   curl -X POST "http://localhost:8085/api/v1/simple/amocrm/setup" \
     -H "Content-Type: application/json" \
     -d '{"domain": "your-account.amocrm.ru", ...}'
   ```

3. **Протестируйте шаблоны:**
   ```bash
   python scripts/test_templates.py
   ```

4. **Проверьте статус:**
   ```bash
   curl -X GET "http://localhost:8085/api/v1/simple/amocrm/status"
   ```

Теперь система полностью готова к работе с современными шаблонами и настроенным AmoCRM плагином! 