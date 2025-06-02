# 🧪 Система автотестов OntoBot

Комплексная система для автоматического тестирования сценариев OntoBot с мокированием Telegram API.

## 🎯 Возможности

- **Полное мокирование Telegram API** - симуляция всех методов бота
- **Реалистичная симуляция пользователей** - разные типы личности и поведения
- **Автоматическое тестирование сценариев** - проверка прохождения диалогов
- **Детальные отчеты** - логи и статистика выполнения тестов
- **Простой запуск** - одной командой

## 📁 Структура файлов

```
tests/
├── telegram_mock_server.py    # Мок Telegram Bot API
├── user_simulator.py          # Симулятор поведения пользователей  
├── ontobot_test_runner.py     # Запуск тестов сценариев
└── README_ONTOBOT_TESTS.md    # Эта документация

run_ontobot_tests.py           # Главный скрипт запуска
```

## 🚀 Быстрый старт

### 1. Установка зависимостей

```bash
pip install aiohttp fastapi uvicorn loguru
```

### 2. Запуск тестов

```bash
# Полный тест (по умолчанию)
python run_ontobot_tests.py

# Быстрый тест только Mock Server
python run_ontobot_tests.py quick
```

### 3. Просмотр результатов

Результаты сохраняются в:
- `logs/ontobot_test_report_YYYYMMDD_HHMMSS.json` - подробный отчет
- `logs/ontobot_tests.log` - логи выполнения тестов
- `logs/telegram_mock.log` - логи Mock Server

## 🤖 Telegram Mock Server

### Возможности

- **Полная имитация Telegram Bot API**
  - `sendMessage` - отправка сообщений
  - `editMessageText` - редактирование сообщений
  - `sendDocument` - отправка документов
  - `answerCallbackQuery` - ответы на callback
  - `getUpdates` - получение обновлений
  - `setWebhook/deleteWebhook` - управление webhook

- **Дополнительные методы для тестирования**
  - `POST /mock/simulate_user_message` - симуляция сообщения от пользователя
  - `POST /mock/simulate_callback_query` - симуляция нажатия кнопки
  - `GET /mock/messages` - получение истории сообщений
  - `GET /mock/stats` - статистика сервера
  - `DELETE /mock/clear` - очистка данных

### Запуск отдельно

```bash
python tests/telegram_mock_server.py
```

Сервер запустится на `http://localhost:8082`

### Пример использования

```python
import aiohttp

# Симуляция сообщения от пользователя
async with aiohttp.ClientSession() as session:
    await session.post("http://localhost:8082/mock/simulate_user_message", json={
        "user_id": 12345,
        "text": "/start",
        "first_name": "Тестовый"
    })
```

## 👤 User Simulator

### Типы пользователей

1. **Активный** - быстро отвечает, амбициозный
2. **Осторожный** - медленно принимает решения
3. **Любопытный** - задает много вопросов

### Готовые профили

```python
from tests.user_simulator import OntoTestUsers

# Получение готовых пользователей
active_user = OntoTestUsers.get_active_user()
cautious_user = OntoTestUsers.get_cautious_user()
curious_user = OntoTestUsers.get_curious_user()
```

### Пример использования

```python
from tests.user_simulator import UserSimulator

simulator = UserSimulator()

# Создание пользователя
user = simulator.create_user(12345, "активный")

# Отправка сообщения
await simulator.send_message(12345, "Привет!")

# Нажатие кнопки
await simulator.click_button(12345, "start_diagnostic")

# Умный ответ на вопрос
response = simulator.get_smart_response(12345, "goals")
```

## 🧪 Test Runner

### Доступные тесты

1. **`test_mr_ontobot_welcome`** - тест приветственного сценария
2. **`test_user_interaction`** - тест взаимодействия пользователя с ботом

### Добавление новых тестов

```python
async def test_my_scenario(self, user_id: int = 12347) -> Dict[str, Any]:
    """Мой новый тест."""
    
    test_name = "my_scenario"
    start_time = time.time()
    
    try:
        # 1. Очистка мок сервера
        await self._clear_mock_server()
        
        # 2. Выполнение сценария
        response = await self._execute_scenario(
            scenario_id="my_scenario_id",
            user_id=user_id,
            context={"test_mode": True}
        )
        
        # 3. Проверки
        success = response.get("success", False)
        
        # 4. Результат
        return {
            "test_name": test_name,
            "success": success,
            "duration": time.time() - start_time,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "test_name": test_name,
            "success": False,
            "error": str(e),
            "duration": time.time() - start_time
        }

# Добавить в список тестов
tests = [
    self.test_mr_ontobot_welcome,
    self.test_user_interaction,
    self.test_my_scenario  # <-- новый тест
]
```

## 📊 Отчеты

### Формат JSON отчета

```json
{
  "test_run": {
    "timestamp": "2024-01-15T10:30:00",
    "total_tests": 2,
    "passed": 1,
    "failed": 1
  },
  "results": [
    {
      "test_name": "mr_ontobot_welcome",
      "success": true,
      "duration": 2.45,
      "messages_count": 3,
      "welcome_message_found": true,
      "timestamp": "2024-01-15T10:30:02"
    },
    {
      "test_name": "user_interaction", 
      "success": false,
      "duration": 1.23,
      "error": "Connection refused",
      "timestamp": "2024-01-15T10:30:05"
    }
  ]
}
```

### Консольный вывод

```
============================================================
🧪 ОТЧЕТ О ТЕСТИРОВАНИИ ONTOBOT
============================================================
📊 Всего тестов: 2
✅ Прошли: 1
❌ Провалились: 1
📈 Успешность: 50.0%
⏱️ Время выполнения: 3.68с
============================================================

❌ ПРОВАЛИВШИЕСЯ ТЕСТЫ:
  • user_interaction: Connection refused

✅ УСПЕШНЫЕ ТЕСТЫ:
  • mr_ontobot_welcome: 2.45с

📄 Подробный отчет сохранен в logs/
============================================================
```

## 🔧 Настройка

### Порты

- **KittyCore API**: `8085` (основной сервис)
- **Telegram Mock Server**: `8082` (для тестов)

### Переменные окружения

```bash
# Опционально - для настройки URL
export KITTYCORE_URL="http://localhost:8085"
export MOCK_SERVER_URL="http://localhost:8082"
```

### Логирование

Все логи сохраняются в папку `logs/`:

- `test_launcher.log` - логи запуска тестов
- `ontobot_tests.log` - логи выполнения тестов
- `telegram_mock.log` - логи Mock Server
- `user_simulator.log` - логи симулятора пользователей

## 🐛 Отладка

### Проверка Mock Server

```bash
curl http://localhost:8082/
curl http://localhost:8082/mock/stats
```

### Проверка KittyCore API

```bash
curl http://localhost:8085/health
curl http://localhost:8085/api/v1/simple/info
```

### Ручная симуляция

```bash
# Отправка сообщения от пользователя
curl -X POST http://localhost:8082/mock/simulate_user_message \
  -H "Content-Type: application/json" \
  -d '{"user_id": 12345, "text": "/start", "first_name": "Тест"}'

# Получение сообщений
curl http://localhost:8082/mock/messages?chat_id=12345
```

## 📝 Примеры использования

### Тестирование конкретного сценария

```python
from tests.ontobot_test_runner import OntoTestRunner

runner = OntoTestRunner()

# Тест конкретного сценария
result = await runner.test_mr_ontobot_welcome(user_id=12345)
print(f"Результат: {result['success']}")
```

### Симуляция диалога

```python
from tests.user_simulator import UserSimulator

simulator = UserSimulator()

# Создаем пользователя
user = simulator.create_user(12345, "любопытный")

# Диалог
await simulator.send_message(12345, "/start")
await simulator.send_message(12345, "Хочу пройти диагностику")
await simulator.click_button(12345, "begin_diagnostic")

# Умные ответы
name = simulator.get_smart_response(12345, "name")
goals = simulator.get_smart_response(12345, "goals")

await simulator.send_message(12345, name)
await simulator.send_message(12345, goals)
```

## 🚀 Интеграция в CI/CD

### GitHub Actions

```yaml
name: OntoBot Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Run OntoBot tests
      run: |
        python run_ontobot_tests.py full
    
    - name: Upload test reports
      uses: actions/upload-artifact@v2
      with:
        name: test-reports
        path: logs/
```

## 🔮 Планы развития

- [ ] Поддержка тестирования голосовых сообщений
- [ ] Интеграция с реальными LLM для более умных ответов
- [ ] Визуальные отчеты с графиками
- [ ] Параллельное выполнение тестов
- [ ] Тестирование производительности
- [ ] Интеграция с Selenium для веб-интерфейса

## 🆘 Поддержка

При возникновении проблем:

1. Проверьте логи в папке `logs/`
2. Убедитесь что KittyCore запущен на порту 8085
3. Проверьте доступность портов 8082 и 8085
4. Запустите быстрый тест: `python run_ontobot_tests.py quick`

---

**Создано для тестирования OntoBot сценариев** 🤖✨ 