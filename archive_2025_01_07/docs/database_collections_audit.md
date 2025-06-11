# Аудит коллекций базы данных Universal Agent Platform

## Проблема
28 мая 2025 года обнаружена критическая проблема с настройками плагинов:
- Настройки AmoCRM находятся в коллекции `settings`
- Плагины ищут настройки в коллекции `plugin_settings`
- Это приводит к ошибкам "отсутствуют настройки"

## Текущее состояние коллекций

### Коллекция `settings` (2 документа)
1. **AmoCRM настройки** - `{plugin_name: "simple_amocrm"}`
   - base_url: `https://ontonothing2025.amocrm.ru`
   - access_token: JWT токен
   - plugin: `simple_amocrm`

2. **Telegram настройки** - `{key: "telegram_default_scenario"}`
   - value: `onto_main_router`
   - description: "Сценарий по умолчанию для Telegram канала"

### Коллекция `plugin_settings` (3 документа)
1. **AmoCRM поля контактов** - `{plugin_name: "amocrm_fields_contacts"}`
2. **Telegram (старый)** - `{plugin_name: "simple_telegram"}`
3. **Telegram (старый)** - `{plugin_name: "telegram"}`

### Другие коллекции
- `scenarios`: 10 документов (ONTO сценарии)
- `channels`: 1 документ (onto_telegram_bot)
- `user_states`: 1 документ (состояния пользователей)
- `onto_users`: 1 документ (пользователи ONTO)

## Несогласованность в плагинах

### ✅ Исправлены (ищут в `settings`)
- `simple_amocrm_plugin.py` - строки 62, 127

### ❌ Требуют исправления (ищут в `plugin_settings`)
- `simple_amocrm_companies.py` - строка 61
- `simple_amocrm_advanced.py` - строка 71
- `simple_amocrm_admin.py` - строка 74
- `simple_amocrm_tasks.py` - строка 61
- `simple_llm_plugin.py` - строка 56

## Решение

### Вариант 1: Единый стандарт `settings`
**Плюсы:**
- Одна коллекция для всех настроек плагинов
- Простота и консистентность
- Настройки AmoCRM уже там

**Минусы:**
- Нужно исправить все плагины
- Нужно мигрировать данные из `plugin_settings`

### Вариант 2: Единый стандарт `plugin_settings`
**Плюсы:**
- Большинство плагинов уже используют эту коллекцию
- Семантически более правильное название

**Минусы:**
- Нужно перенести настройки AmoCRM
- Конфликт с текущими настройками

### Вариант 3: Гибридный поиск
**Плюсы:**
- Обратная совместимость
- Плавный переход

**Минусы:**
- Усложнение логики
- Потенциальная путаница

## Рекомендации

1. **Принять Вариант 1** - использовать коллекцию `settings` для всех плагинов
2. **Создать migration script** для переноса данных из `plugin_settings` в `settings`
3. **Исправить все плагины** чтобы они искали настройки в `settings`
4. **Добавить валидацию** при инициализации плагинов
5. **Документировать стандарт** в архитектурных принципах

## Структура документа настроек (стандарт)

```json
{
  "plugin_name": "simple_amocrm",
  "base_url": "https://ontonothing2025.amocrm.ru",
  "access_token": "JWT_TOKEN",
  "created_at": "2024-01-28T00:00:00Z",
  "updated_at": "2024-01-28T00:00:00Z",
  "description": "Настройки AmoCRM плагина"
}
```

## План исправления

1. ✅ Исправить `simple_amocrm_plugin.py` (уже сделано)
2. ❌ Исправить `simple_amocrm_companies.py`
3. ❌ Исправить `simple_amocrm_advanced.py`
4. ❌ Исправить `simple_amocrm_admin.py`
5. ❌ Исправить `simple_amocrm_tasks.py`
6. ❌ Исправить `simple_llm_plugin.py`
7. ❌ Мигрировать данные из `plugin_settings` в `settings`
8. ❌ Удалить устаревшие записи из `plugin_settings`
9. ❌ Добавить тесты на согласованность
10. ❌ Обновить документацию 