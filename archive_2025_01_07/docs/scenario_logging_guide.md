# 🔍 Система логирования сценариев

Комплексная система детального логирования каждого шага выполнения сценариев с поддержкой разных уровней детализации, сохранения в файлы и MongoDB, а также анализа производительности.

## 📋 Возможности

### ✅ Что уже реализовано:

1. **Детальное логирование каждого шага**
   - Время начала и завершения каждого шага
   - Длительность выполнения в миллисекундах
   - Статус выполнения (success, error, stopped)
   - Параметры шага и результаты

2. **Разные уровни детализации**
   - `MINIMAL` - только начало/конец сценария
   - `BASIC` - + каждый шаг (по умолчанию)
   - `DETAILED` - + параметры и результаты шагов
   - `FULL` - + полный контекст на каждом шаге

3. **Множественные места хранения**
   - Структурированные логи в файл `logs/scenario_execution.log`
   - Сохранение в MongoDB коллекцию `scenario_execution_logs`
   - Интеграция с общей системой логирования loguru

4. **Метрики производительности**
   - Общее время выполнения сценария
   - Средняя/максимальная/минимальная длительность шагов
   - Процент успешности выполнения
   - Самые медленные и быстрые шаги

5. **API для мониторинга**
   - Просмотр активных выполнений
   - Детали конкретного выполнения
   - История выполнений с фильтрацией

## 🚀 Использование

### Автоматическое логирование

Логирование включается автоматически для всех сценариев, выполняемых через `SimpleScenarioEngine`. Никаких дополнительных действий не требуется.

```python
# Обычное выполнение сценария - логирование включено автоматически
result = await engine.execute_scenario(scenario, context)
```

### Настройка уровня детализации

```python
from app.core.scenario_logger import initialize_scenario_logger, LogLevel

# Инициализация с детальным логированием
initialize_scenario_logger(
    log_level=LogLevel.DETAILED,  # или MINIMAL, BASIC, FULL
    mongo_plugin=mongo_plugin
)
```

### Переменные окружения

```bash
# Включить максимальную детализацию в режиме отладки
DEBUG=true
```

## 📊 Структура логов

### Лог сценария (ScenarioLog)

```json
{
  "execution_id": "uuid-строка",
  "scenario_id": "имя_сценария",
  "user_id": "id_пользователя",
  "chat_id": "id_чата",
  "channel_id": "id_канала",
  "started_at": "2024-01-01T12:00:00.000Z",
  "finished_at": "2024-01-01T12:00:05.123Z",
  "duration_ms": 5123.45,
  "status": "completed",
  "total_steps": 5,
  "completed_steps": 5,
  "initial_context": {...},
  "final_context": {...},
  "steps": [...],
  "performance_metrics": {...}
}
```

### Лог шага (StepLog)

```json
{
  "step_id": "send_message",
  "step_type": "channel_action",
  "started_at": "2024-01-01T12:00:01.000Z",
  "finished_at": "2024-01-01T12:00:01.234Z",
  "duration_ms": 234.56,
  "status": "success",
  "error_message": null,
  "step_params": {...},
  "context_before": {...},
  "context_after": {...},
  "context_changes": {
    "added": {...},
    "modified": {...},
    "removed": [...]
  }
}
```

### Метрики производительности

```json
{
  "total_duration_ms": 5123.45,
  "steps_count": 5,
  "success_rate": 100.0,
  "avg_step_duration_ms": 1024.69,
  "max_step_duration_ms": 2000.12,
  "min_step_duration_ms": 45.23,
  "slowest_step": {
    "id": "llm_query",
    "type": "llm_query",
    "duration_ms": 2000.12
  },
  "fastest_step": {
    "id": "start",
    "type": "start", 
    "duration_ms": 45.23
  }
}
```

## 🌐 API Endpoints

### Активные выполнения

```http
GET /api/v1/simple/scenario-logs/active
```

**Ответ:**
```json
{
  "success": true,
  "active_scenarios": [
    {
      "execution_id": "uuid",
      "scenario_id": "registration",
      "user_id": "123",
      "status": "running",
      "started_at": "2024-01-01T12:00:00.000Z",
      "duration_ms": 1234.56,
      "total_steps": 10,
      "completed_steps": 7,
      "current_step": "validate_phone"
    }
  ],
  "count": 1
}
```

### Детали выполнения

```http
GET /api/v1/simple/scenario-logs/{execution_id}
```

**Ответ:**
```json
{
  "success": true,
  "log": {
    "execution_id": "uuid",
    "scenario_id": "registration",
    "steps": [
      {
        "step_id": "start",
        "step_type": "start",
        "started_at": "2024-01-01T12:00:00.000Z",
        "finished_at": "2024-01-01T12:00:00.123Z",
        "duration_ms": 123.45,
        "status": "success"
      }
    ],
    "performance_metrics": {...}
  }
}
```

### История выполнений

```http
GET /api/v1/simple/scenario-logs/history?limit=50&scenario_id=registration&user_id=123
```

**Параметры:**
- `limit` - количество записей (по умолчанию 50)
- `scenario_id` - фильтр по ID сценария
- `user_id` - фильтр по ID пользователя

## 📁 Файлы логов

### Основные логи

- `logs/scenario_execution.log` - детальные логи выполнения сценариев
- `logs/api.log` - логи API запросов
- `logs/errors.log` - логи ошибок системы

### Формат логов

```
2024-01-01 12:00:00.123 | INFO | SCENARIO | 🎬 НАЧАЛО СЦЕНАРИЯ registration | execution_id=uuid | scenario_id=registration | user_id=123
2024-01-01 12:00:00.234 | INFO | SCENARIO | ▶️ ШАГ start (start) | execution_id=uuid | step_id=start | step_type=start
2024-01-01 12:00:00.345 | INFO | SCENARIO | ✅ ШАГ start завершен (111.2ms) | execution_id=uuid | step_id=start | status=success
```

## 🧪 Тестирование

### Запуск тестов

```bash
# Тест системы логирования
python test_scenario_logging.py
```

### Пример тестового сценария

```python
test_scenario = {
    "scenario_id": "test_logging",
    "steps": [
        {
            "id": "start",
            "type": "start",
            "next_step": "log_message"
        },
        {
            "id": "log_message",
            "type": "log_message",
            "params": {
                "message": "Тестовое сообщение: {user_name}",
                "level": "INFO"
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

## 🔧 Настройка

### Уровни логирования

```python
from app.core.scenario_logger import LogLevel

# MINIMAL - только начало/конец сценария
LogLevel.MINIMAL

# BASIC - + каждый шаг (по умолчанию)
LogLevel.BASIC  

# DETAILED - + параметры и результаты
LogLevel.DETAILED

# FULL - + полный контекст на каждом шаге
LogLevel.FULL
```

### Интеграция с MongoDB

```python
# Автоматическая инициализация при старте системы
await initialize_global_engine()

# Логи автоматически сохраняются в коллекцию scenario_execution_logs
```

## 📈 Мониторинг и анализ

### Ключевые метрики

1. **Производительность**
   - Время выполнения сценариев
   - Самые медленные шаги
   - Узкие места в логике

2. **Надежность**
   - Процент успешных выполнений
   - Частые ошибки
   - Места остановки сценариев

3. **Использование**
   - Популярные сценарии
   - Активность пользователей
   - Паттерны использования

### Анализ через MongoDB

```javascript
// Самые медленные сценарии
db.scenario_execution_logs.find().sort({"duration_ms": -1}).limit(10)

// Сценарии с ошибками
db.scenario_execution_logs.find({"status": "error"})

// Статистика по сценариям
db.scenario_execution_logs.aggregate([
  {$group: {
    _id: "$scenario_id",
    count: {$sum: 1},
    avg_duration: {$avg: "$duration_ms"},
    success_rate: {$avg: {$cond: [{$eq: ["$status", "completed"]}, 1, 0]}}
  }}
])
```

## 🚨 Устранение неполадок

### Логи не сохраняются

1. Проверьте инициализацию системы:
```python
await initialize_global_engine()
```

2. Проверьте права на запись в папку `logs/`

3. Проверьте подключение к MongoDB для сохранения структурированных данных

### Слишком много логов

1. Уменьшите уровень детализации:
```python
initialize_scenario_logger(log_level=LogLevel.MINIMAL)
```

2. Настройте ротацию логов в `loguru`

### Производительность

1. Логирование добавляет минимальные накладные расходы (~1-5ms на шаг)
2. Для критичных по производительности сценариев используйте `LogLevel.MINIMAL`
3. MongoDB операции выполняются асинхронно и не блокируют выполнение

## 🔮 Планы развития

1. **Дашборд для мониторинга** - веб-интерфейс для просмотра логов
2. **Алерты** - уведомления о критических ошибках
3. **Экспорт данных** - выгрузка логов в различных форматах
4. **Интеграция с метриками** - Prometheus/Grafana
5. **Машинное обучение** - анализ паттернов и аномалий 