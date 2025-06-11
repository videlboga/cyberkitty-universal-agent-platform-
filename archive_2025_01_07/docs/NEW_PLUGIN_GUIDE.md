# 🔌 РУКОВОДСТВО ПО СОЗДАНИЮ ПЛАГИНОВ

## 🎯 **ЦЕЛЬ:**
Создание универсальных плагинов для современной Universal Agent Platform

---

## 🏗️ **СОВРЕМЕННАЯ АРХИТЕКТУРА ПЛАГИНОВ:**

### **✅ СТАНДАРТ (Обязательно для всех плагинов):**

```python
from app.core.base_plugin import BasePlugin
from typing import Dict, Any, Callable
from loguru import logger

class MyNewPlugin(BasePlugin):
    """
    Современный плагин для Universal Agent System
    
    ОБЯЗАТЕЛЬНЫЕ МЕТОДЫ:
    - register_handlers() - регистрация типов шагов
    - healthcheck() - проверка работоспособности
    
    ОПЦИОНАЛЬНЫЕ МЕТОДЫ:
    - initialize() - асинхронная инициализация
    - get_default_config() - конфигурация по умолчанию
    - get_config_description() - описание параметров
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__()
        self.config = config or {}
        self.name = self.__class__.__name__
        logger.info(f"🔌 {self.name} инициализирован")
    
    def register_handlers(self) -> Dict[str, Callable]:
        """
        ОБЯЗАТЕЛЬНЫЙ МЕТОД: Регистрация обработчиков шагов
        
        Returns:
            Dict[str, Callable]: Словарь {step_type: handler_function}
        """
        handlers = {
            "my_action": self.handle_my_action,
            "my_request": self.handle_my_request
        }
        
        logger.info(f"✅ {self.name} зарегистрировал: {list(handlers.keys())}")
        return handlers
    
    async def handle_my_action(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        """
        СТАНДАРТНАЯ СИГНАТУРА обработчика шага
        
        Args:
            step_data: Данные шага из сценария
            context: Контекст сценария (изменяется in-place)
        
        Returns:
            None - ВСЕГДА возвращать None
        """
        params = step_data.get("params", {})
        
        try:
            # Ваша логика здесь
            result = self._execute_my_logic(params)
            
            # Сохраняем результат в контекст
            output_var = params.get("output_var", "my_result")
            context[output_var] = result
            
            logger.info(f"🎯 {self.name}.handle_my_action: Успешно выполнено")
            
        except Exception as e:
            logger.error(f"❌ {self.name}.handle_my_action: Ошибка: {e}")
            context["__step_error__"] = f"{self.name}: {str(e)}"
        
        return None  # ОБЯЗАТЕЛЬНО!
        
    async def healthcheck(self) -> bool:
        """
        ОБЯЗАТЕЛЬНЫЙ МЕТОД: Проверка работоспособности
        
        Returns:
            bool: True если плагин работает, False если есть проблемы
        """
        try:
            # Проверьте доступность внешних сервисов, API ключи и т.д.
            logger.info(f"✅ {self.name} healthcheck: OK")
            return True
            
        except Exception as e:
            logger.error(f"❌ {self.name} healthcheck: FAIL - {e}")
            return False
```

---

## 🔧 **СОВРЕМЕННЫЕ ТИПЫ ШАГОВ:**

### **📋 БАЗОВЫЕ ОБРАБОТЧИКИ (13 штук):**

```python
# === ЖИЗНЕННЫЙ ЦИКЛ ===
"start"              # Начало сценария
"end"                # Завершение сценария

# === ЛОГИКА ===
"action"             # Универсальные действия через плагины
"input"              # Ожидание ввода пользователя
"branch"             # Современные условные переходы
"switch_scenario"    # Переключение сценариев
"log_message"        # Логирование сообщений

# === УНИВЕРСАЛЬНЫЕ КАНАЛЫ ===
"channel_send_message"    # Отправка сообщения
"channel_send_buttons"    # Отправка кнопок
"channel_edit_message"    # Редактирование сообщения
"channel_start_polling"   # Запуск polling
"channel_update_token"    # Обновление токена
"channel_load_token"      # Загрузка токена
```

---

## 📋 **ШАБЛОН СОВРЕМЕННОГО СЦЕНАРИЯ:**

```json
{
  "scenario_id": "modern_example",
  "name": "Современный пример", 
  "description": "Демонстрация современной архитектуры",
  "version": "3.0.0",
  "steps": [
    {
      "id": "start",
      "type": "start",
      "next_step": "welcome"
    },
    {
      "id": "welcome",
      "type": "channel_send_message",
      "params": {
        "channel_id": "{channel_id}",
        "chat_id": "{chat_id}",
        "text": "Добро пожаловать!",
        "output_var": "welcome_result"
      },
      "next_step": "llm_request"
    },
    {
      "id": "llm_request",
      "type": "action",
      "params": {
        "action": "llm_chat",
        "prompt": "Ответь пользователю: {user_message}",
        "output_var": "llm_response"
      },
      "next_step": "send_response"
    },
    {
      "id": "send_response",
      "type": "channel_send_message",
      "params": {
        "channel_id": "{channel_id}",
        "chat_id": "{chat_id}",
        "text": "{llm_response}",
        "output_var": "response_result"
      },
      "next_step": "end"
    },
    {
      "id": "end",
      "type": "end",
      "params": {
        "message": "Сценарий завершен"
      }
    }
  ]
}
```

---

## 🧪 **ИНТЕГРАЦИЯ И ТЕСТИРОВАНИЕ:**

### **Шаг 1: Создайте плагин**
```python
# app/plugins/my_new_plugin.py
from app.core.base_plugin import BasePlugin
# ... код плагина из шаблона выше
```

### **Шаг 2: Добавьте в create_engine()**
```python
# В app/core/simple_engine.py функция create_engine()
try:
    from app.plugins.my_new_plugin import MyNewPlugin
    my_plugin = MyNewPlugin()
    engine.register_plugin(my_plugin)
    plugins_to_initialize.append(my_plugin)
    logger.info("✅ MyNewPlugin зарегистрирован")
except Exception as e:
    logger.warning(f"⚠️ MyNewPlugin недоступен: {e}")
```

### **Шаг 3: Протестируйте**
```python
import asyncio
from app.core.simple_engine import create_engine

async def test():
    engine = await create_engine()
    handlers = engine.get_registered_handlers()
    print(f"Обработчиков: {len(handlers)}")
    print(f"Ваши обработчики: {[h for h in handlers if h.startswith('my_')]}")

asyncio.run(test())
```

---

## 🚀 **ПРИМЕРЫ ПОПУЛЯРНЫХ ПЛАГИНОВ:**

### **1. LLM Plugin**
```python
class SimpleLLMPlugin(BasePlugin):
    def register_handlers(self):
        return {
            "llm_chat": self.handle_llm_chat,
            "llm_generate": self.handle_llm_generate
        }
```

### **2. Database Plugin**  
```python
class MongoPlugin(BasePlugin):
    def register_handlers(self):
        return {
            "mongo_find": self.handle_mongo_find,
            "mongo_insert": self.handle_mongo_insert,
            "mongo_update": self.handle_mongo_update
        }
```

### **3. HTTP Plugin**
```python
class SimpleHTTPPlugin(BasePlugin):
    def register_handlers(self):
        return {
            "http_get": self.handle_http_get,
            "http_post": self.handle_http_post
        }
```

---

## 🛡️ **BEST PRACTICES:**

### **Безопасность:**
- 🔐 API ключи только через переменные окружения
- 🛡️ Валидация всех входных параметров
- 🔍 Логирование без секретных данных

### **Производительность:**
- ⚡ Асинхронные операции везде где возможно
- 🔄 Переиспользование соединений
- ⏱️ Тайм-ауты для внешних вызовов

### **Надежность:**
- 🔁 Retry logic для временных сбоев
- 📊 Подробные ошибки в логах  
- 🏥 Graceful degradation при недоступности сервиса

---

## 📞 **ПОДДЕРЖКА:**

### **Документация:**
- 📖 `docs/NEW_PLUGIN_GUIDE.md` - это руководство
- 🏗️ `app/core/simple_engine.py` - современная архитектура

### **Примеры:**
- 💡 `app/plugins/simple_llm_plugin.py` - LLM интеграция
- 🔗 `app/plugins/simple_telegram_plugin.py` - Telegram API
- 💾 `app/plugins/mongo_plugin.py` - работа с базой данных

**Создавайте современные плагины! 🚀** 