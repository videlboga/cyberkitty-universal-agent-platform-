# 📋 Модульная архитектура AmoCRM плагинов

## 🎯 Обзор

Система AmoCRM разделена на 5 специализированных модулей для лучшей организации и поддержки кода:

- **Базовый модуль** - основные операции с контактами и сделками
- **Модуль компаний** - работа с компаниями
- **Модуль задач** - задачи и события
- **Продвинутый модуль** - вебхуки, виджеты, звонки, каталоги
- **Административный модуль** - воронки, поля, пользователи, теги

## 📦 Модули и их handlers

### 1. Базовый модуль (`simple_amocrm_plugin.py`)
**6 handlers для основных операций:**

- `amocrm_find_contact` - поиск контакта по query
- `amocrm_create_contact` - создание контакта (name, phone, email)
- `amocrm_find_lead` - поиск сделки по query
- `amocrm_create_lead` - создание сделки (name, price, contact_id)
- `amocrm_add_note` - добавление заметки к сущности
- `amocrm_search` - универсальный поиск (contacts, leads)

### 2. Модуль компаний (`simple_amocrm_companies.py`)
**8 handlers для работы с компаниями:**

- `amocrm_list_companies` - список компаний с фильтрацией
- `amocrm_get_company` - получение компании по ID
- `amocrm_create_company` - создание новой компании
- `amocrm_update_company` - обновление компании
- `amocrm_delete_company` - удаление компании
- `amocrm_add_company_contact` - привязка контакта к компании
- `amocrm_remove_company_contact` - отвязка контакта от компании
- `amocrm_get_company_contacts` - получение контактов компании

### 3. Модуль задач (`simple_amocrm_tasks.py`)
**8 handlers для задач и событий:**

- `amocrm_create_task` - создание задачи с привязкой к сущности
- `amocrm_update_task` - обновление задачи
- `amocrm_complete_task` - завершение задачи с результатом
- `amocrm_get_task` - получение задачи по ID
- `amocrm_list_tasks` - список задач с фильтрацией
- `amocrm_delete_task` - удаление задачи
- `amocrm_create_event` - создание события
- `amocrm_list_events` - список событий

### 4. Продвинутый модуль (`simple_amocrm_advanced.py`)
**12 handlers для продвинутых функций:**

**Вебхуки:**
- `amocrm_list_webhooks` - список вебхуков
- `amocrm_create_webhook` - создание вебхука
- `amocrm_update_webhook` - обновление вебхука
- `amocrm_delete_webhook` - удаление вебхука

**Виджеты:**
- `amocrm_list_widgets` - список виджетов
- `amocrm_install_widget` - установка виджета
- `amocrm_uninstall_widget` - удаление виджета

**Звонки:**
- `amocrm_create_call` - создание записи о звонке
- `amocrm_list_calls` - список звонков

**Каталоги:**
- `amocrm_list_catalogs` - список каталогов
- `amocrm_create_catalog` - создание каталога
- `amocrm_list_catalog_elements` - элементы каталога
- `amocrm_create_catalog_element` - создание элемента каталога

### 5. Административный модуль (`simple_amocrm_admin.py`)
**14 handlers для административных операций:**

**Воронки:**
- `amocrm_list_pipelines` - список воронок
- `amocrm_get_pipeline` - получение воронки по ID
- `amocrm_create_pipeline` - создание воронки
- `amocrm_update_pipeline` - обновление воронки

**Статусы:**
- `amocrm_list_statuses` - список статусов воронки
- `amocrm_create_status` - создание статуса
- `amocrm_update_status` - обновление статуса

**Пользователи:**
- `amocrm_list_users` - список пользователей
- `amocrm_get_user` - получение пользователя по ID

**Кастомные поля:**
- `amocrm_list_custom_fields` - список кастомных полей
- `amocrm_create_custom_field` - создание кастомного поля
- `amocrm_update_custom_field` - обновление кастомного поля

**Теги:**
- `amocrm_list_tags` - список тегов
- `amocrm_create_tag` - создание тега

## 🏗️ Архитектурные принципы

### Единая архитектура
Все модули следуют единой архитектуре:
- Наследуют от `BasePlugin`
- Делегируют HTTP запросы базовому плагину через `self.base_plugin`
- Получают ссылку на базовый плагин в `_do_initialize()`
- Используют методы `_make_request()` и `_resolve_value()` базового плагина

### Разделение ответственности
- **Базовый плагин** - HTTP клиент, настройки, базовые операции
- **Специализированные модули** - конкретные бизнес-операции
- **Движок** - регистрация и координация всех модулей

### Динамическая загрузка настроек
- Все плагины загружают настройки из БД при каждом запросе
- Метод `_ensure_fresh_settings()` вызывается перед каждым запросом
- НЕ кешируют настройки в памяти плагина

## 📊 Статистика

- **Всего модулей:** 5
- **Всего handlers:** 48
- **Покрытие API AmoCRM:** ~80% основных операций
- **Размер кода:** ~2000 строк (оптимизированно)

## 🚀 Использование

Все модули автоматически регистрируются в движке при запуске:

```python
# Создание движка с модулями AmoCRM
engine = await create_engine()

# Все handlers доступны сразу
handlers = engine.get_registered_handlers()
amocrm_handlers = [h for h in handlers if h.startswith('amocrm_')]
```

## 🔧 Настройка

Настройки хранятся в MongoDB в коллекции `agent_settings`:

```json
{
  "agent_id": "amocrm_agent",
  "settings": {
    "amocrm_subdomain": "your-subdomain",
    "amocrm_client_id": "your-client-id",
    "amocrm_client_secret": "your-client-secret",
    "amocrm_redirect_uri": "your-redirect-uri",
    "amocrm_access_token": "your-access-token",
    "amocrm_refresh_token": "your-refresh-token"
  }
}
```

## ✅ Статус модулей

- ✅ **Базовый модуль** - готов и протестирован
- ✅ **Модуль компаний** - готов и протестирован  
- ✅ **Модуль задач** - готов и протестирован
- ✅ **Продвинутый модуль** - готов и протестирован
- ✅ **Административный модуль** - готов и протестирован

Все модули зарегистрированы в движке и готовы к использованию! 