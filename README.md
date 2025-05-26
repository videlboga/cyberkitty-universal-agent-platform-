# 🎯 Universal Agent Platform

**Универсальная платформа для создания ИИ-агентов**

**Принцип:** ПРОСТОТА ПРЕВЫШЕ ВСЕГО! 

> ✅ **Рефакторинг завершён!** Архитектура упрощена на 70%. Все устаревшие компоненты перемещены в `archive/`.

## 🏗️ Упрощённая архитектура

```
SimpleScenarioEngine (единственный движок)
├── Базовые обработчики (start, end, action, input, conditional_execute)
└── Плагин-специфичные обработчики:
    ├── SimpleTelegramPlugin (telegram_send_message, telegram_send_buttons)
    ├── MongoPlugin (mongo_save, mongo_get)
    └── SimpleOrchestratorPlugin (switch_scenario)

SimpleTelegramIntegration (единый интеграционный слой)
└── Обработка всех Telegram событий

Simple API (app/api/simple.py)
└── POST /agents/{agent_id}/execute (единственный endpoint)
```

## 🎯 Принципы новой архитектуры

1. ✅ **Один движок** вместо множества
2. ✅ **Простая система плагинов** через BasePlugin
3. ✅ **Один API endpoint** вместо множества
4. ✅ **Минимум зависимостей** и абстракций
5. ✅ **Явная передача контекста** между компонентами
6. ✅ **Разделение ответственности** - движок универсален, плагины специализированы

## 📁 Структура проекта

### Активные компоненты:
```
app/
├── core/
│   ├── simple_engine.py              # Единственный движок
│   ├── base_plugin.py                # Базовый класс плагинов
│   └── simple_telegram_integration.py # Telegram интеграция
├── plugins/
│   ├── simple_telegram_plugin.py     # Telegram плагин
│   ├── mongo_plugin.py               # MongoDB плагин
│   └── simple_orchestrator_plugin.py # Оркестратор сценариев
├── api/
│   └── simple.py                     # Единый API
├── simple_dependencies.py            # Простые зависимости
└── simple_main.py                    # Главный файл
```

### Демонстрационные материалы:
- `telegram_scenario_refactored.js` - Демо-сценарий новой архитектуры
- `test_refactored_architecture.py` - Тест рефакторинга
- `REFACTORING_REPORT.md` - Подробный отчёт о рефакторинге

### Архив:
- `archive/` - Все устаревшие компоненты (70% кода)

## 🚀 Быстрый старт

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 2. Настройка переменных окружения

```bash
# Опционально - для полной функциональности
export TELEGRAM_BOT_TOKEN="your_bot_token"
export MONGODB_URI="mongodb://localhost:27017"
```

### 3. Запуск системы

```bash
# Запуск простого API
python app/simple_main.py

# Или запуск тестов
python test_refactored_architecture.py
```

## 📋 API

### Единственный endpoint:

**POST /agents/{agent_id}/execute**

```json
{
  "user_id": "123456789",
  "chat_id": "987654321", 
  "context": {
    "user_name": "Пользователь",
    "message_text": "/start"
  }
}
```

**Response:**
```json
{
  "success": true,
  "scenario_id": "simple_telegram",
  "final_context": {...},
  "message": "Сценарий выполнен успешно"
}
```

## 🎬 Типы шагов сценариев

### Базовые (в движке):
- `start` - Начало сценария
- `end` - Завершение сценария  
- `action` - Выполнение действий
- `input` - Ожидание ввода
- `conditional_execute` - Условная логика

### Telegram (в плагине):
- `telegram_send_message` - Отправка сообщений
- `telegram_send_buttons` - Отправка кнопок
- `telegram_edit_message` - Редактирование сообщений

### MongoDB (в плагине):
- `mongo_save` - Сохранение данных
- `mongo_get` - Получение данных

### Оркестрация (в плагине):
- `switch_scenario` - Переключение сценариев

## 📝 Пример сценария

```javascript
{
  "scenario_id": "simple_demo",
  "steps": [
    {
      "id": "start",
      "type": "start",                    // Базовый тип - в движке
      "next_step": "welcome"
    },
    {
      "id": "welcome", 
      "type": "telegram_send_message",    // Плагин-специфичный тип
      "params": {
        "chat_id": "{chat_id}",
        "text": "Привет, {user_name}!"
      },
      "next_step": "check_role"
    },
    {
      "id": "check_role",
      "type": "conditional_execute",      // Базовый тип - в движке
      "params": {
        "condition": "user_role == 'admin'",
        "true_step": "admin_menu",
        "false_step": "user_menu"
      }
    },
    {
      "id": "end",
      "type": "end"                       // Базовый тип - в движке
    }
  ]
}
```

## 🧪 Тестирование

```bash
# Тест новой архитектуры
python test_refactored_architecture.py

# Проверка здоровья системы
curl http://localhost:8080/simple/health
```

## 📊 Результаты рефакторинга

| Метрика | До | После | Улучшение |
|---------|----|----|-----------|
| Файлов | 78 | 24 | -70% |
| Движков | 5 | 1 | -80% |
| API endpoints | 9 | 1 | -89% |
| Плагинов | 14 | 3 | -79% |

## 🚫 Что НЕ нужно восстанавливать

- Множественные движки (atomic, extensible, hybrid, unified)
- Сложные адаптеры и обёртки  
- Дублирующиеся API endpoints
- Избыточные сервисы
- Сложные системы зависимостей

**Все устаревшие компоненты находятся в `archive/` для справки.**

## 📚 Документация

- `REFACTORING_REPORT.md` - Подробный отчёт о рефакторинге
- `archive/README.md` - Описание архивированных компонентов
- `telegram_scenario_refactored.js` - Демо-сценарий

---

**Помните: Простота превыше всего!** 🎯 