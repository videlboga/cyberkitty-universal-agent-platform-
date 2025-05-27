# 🔌 РУКОВОДСТВО ПО СОЗДАНИЮ НОВЫХ ПЛАГИНОВ

## 🎯 **ЦЕЛЬ:**
Создание универсального и расширяемого интерфейса для новых плагинов, который будет работать со всеми типами движков

---

## 🏗️ **АРХИТЕКТУРА ПЛАГИНОВ:**

### **✅ ТЕКУЩИЙ СТАНДАРТ (Обязательно для всех плагинов):**

```python
from app.core.base_plugin import BasePlugin
from typing import Dict, Any, Callable
from loguru import logger

class MyNewPlugin(BasePlugin):
    """
    Новый плагин для Universal Agent System
    
    ОБЯЗАТЕЛЬНЫЕ МЕТОДЫ:
    - register_step_handlers() - регистрация типов шагов
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
        
        # Логируем зарегистрированные типы
        logger.info(f"✅ {self.name} зарегистрировал: {list(handlers.keys())}")
        return handlers
    
    async def handle_my_action(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        """
        СТАНДАРТНАЯ СИГНАТУРА обработчика шага
        
        Args:
            step_data: Данные шага из сценария
                {
                    "id": "step_id",
                    "type": "my_action", 
                    "params": {...}
                }
            context: Контекст сценария (изменяется in-place)
        
        Returns:
            None - ВСЕГДА возвращать None
            
        ВАЖНО:
        - Результаты сохранять в context, НЕ возвращать
        - Ошибки сохранять в context["__step_error__"]
        - Логировать все важные события
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
    
    async def handle_my_request(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Другой тип шага"""
        # Аналогичная логика...
        return None
        
    async def healthcheck(self) -> bool:
        """
        ОБЯЗАТЕЛЬНЫЙ МЕТОД: Проверка работоспособности
        
        Returns:
            bool: True если плагин работает, False если есть проблемы
        """
        try:
            # Проверьте доступность внешних сервисов, API ключи и т.д.
            # Например:
            # await self._test_api_connection()
            
            logger.info(f"✅ {self.name} healthcheck: OK")
            return True
            
        except Exception as e:
            logger.error(f"❌ {self.name} healthcheck: FAIL - {e}")
            return False
    
    # ===== ДОПОЛНИТЕЛЬНЫЕ МЕТОДЫ (РЕКОМЕНДУЕМЫЕ) =====
    
    async def initialize(self, app: Any = None):
        """
        ОПЦИОНАЛЬНЫЙ: Асинхронная инициализация
        Вызывается автоматически при запуске системы
        """
        logger.info(f"🚀 {self.name} инициализация...")
        # Ваша логика инициализации
        
    def get_default_config(self) -> Dict[str, Any]:
        """ОПЦИОНАЛЬНЫЙ: Конфигурация по умолчанию"""
        return {
            "api_key": "YOUR_API_KEY",
            "base_url": "https://api.example.com",
            "timeout": 30
        }
    
    def get_config_description(self) -> Dict[str, str]:
        """ОПЦИОНАЛЬНЫЙ: Описание параметров конфигурации"""
        return {
            "api_key": "API ключ для внешнего сервиса",
            "base_url": "Базовый URL API",
            "timeout": "Тайм-аут запросов в секундах"
        }
    
    def _execute_my_logic(self, params: Dict[str, Any]) -> Any:
        """Приватные методы для внутренней логики"""
        # Ваша основная логика
        return {"status": "success", "data": "example"}
```

---

## 🔧 **СОВМЕСТИМОСТЬ С НОВЫМИ ДВИЖКАМИ:**

### **🔀 ГИБРИДНЫЙ ДВИЖОК (HybridScenarioEngine)**
✅ **Автоматическая совместимость** - никаких изменений не нужно

### **🔌 АДАПТЕР ПЛАГИНОВ (PluginCompatibilityEngine)**  
✅ **Автоматическая совместимость** - создает адаптеры автоматически

### **⚡ ПРОСТОЙ ДВИЖОК (SimpleScenarioEngine)**
⚠️ **Требует расширение** - добавим поддержку в следующем этапе

---

## 📋 **ШАБЛОН СЦЕНАРИЯ ДЛЯ НОВОГО ПЛАГИНА:**

```json
{
  "scenario_id": "test_my_new_plugin",
  "name": "Тест нового плагина", 
  "description": "Демонстрация возможностей MyNewPlugin",
  "steps": [
    {
      "id": "start_step",
      "type": "log_message",
      "params": {
        "message": "Начинаем тест нового плагина",
        "level": "INFO"
      },
      "next_step": "my_action_step"
    },
    {
      "id": "my_action_step",
      "type": "my_action",
      "params": {
        "input_data": "Тестовые данные",
        "mode": "demo",
        "output_var": "action_result"
      },
      "next_step": "my_request_step"
    },
    {
      "id": "my_request_step", 
      "type": "my_request",
      "params": {
        "query": "Получить данные для {action_result}",
        "format": "json",
        "output_var": "request_result"
      },
      "next_step": "final_step"
    },
    {
      "id": "final_step",
      "type": "log_message",
      "params": {
        "message": "Результат: {request_result}",
        "level": "INFO"
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
from app.plugins.plugin_base import PluginBase
# ... код плагина из шаблона выше
```

### **Шаг 2: Добавьте в dependencies.py**
```python
# app/core/dependencies.py

# Импорт
from app.plugins.my_new_plugin import MyNewPlugin

# Инициализация
my_new_plugin_instance = MyNewPlugin({
    "api_key": os.getenv("MY_API_KEY"),
    "base_url": "https://api.example.com"
})

# Добавьте в список плагинов для ScenarioExecutor
plugins_list = [
    # ... существующие плагины
    my_new_plugin_instance
]
```

### **Шаг 3: Протестируйте совместимость**
```python
# test_my_plugin_compatibility.py

import asyncio
from app.core.plugin_adapter import test_plugin_compatibility
from app.plugins.my_new_plugin import MyNewPlugin

async def test():
    plugin = MyNewPlugin()
    await test_plugin_compatibility([plugin])

asyncio.run(test())
```

### **Шаг 4: Создайте unit-тесты**
```python
# tests/test_my_new_plugin.py

import pytest
from app.plugins.my_new_plugin import MyNewPlugin

@pytest.mark.asyncio
async def test_my_action():
    plugin = MyNewPlugin()
    
    step_data = {
        "id": "test_step",
        "type": "my_action",
        "params": {"input_data": "test"}
    }
    context = {}
    
    await plugin.handle_my_action(step_data, context)
    
    assert "my_result" in context
    assert context.get("__step_error__") is None

@pytest.mark.asyncio  
async def test_healthcheck():
    plugin = MyNewPlugin()
    result = await plugin.healthcheck()
    assert result is True
```

---

## 🚀 **ПРИМЕРЫ ПОПУЛЯРНЫХ ТИПОВ ПЛАГИНОВ:**

### **1. API Интеграция**
```python
class APIPlugin(BasePlugin):
    def register_handlers(self):
        step_handlers["api_call"] = self.handle_api_call
        step_handlers["api_upload"] = self.handle_api_upload
```

### **2. База данных**  
```python
class DatabasePlugin(PluginBase):
    def register_step_handlers(self, step_handlers):
        step_handlers["db_query"] = self.handle_db_query
        step_handlers["db_insert"] = self.handle_db_insert
        step_handlers["db_update"] = self.handle_db_update
```

### **3. Обработка файлов**
```python
class FilePlugin(PluginBase):
    def register_step_handlers(self, step_handlers):
        step_handlers["file_read"] = self.handle_file_read
        step_handlers["file_process"] = self.handle_file_process
        step_handlers["file_convert"] = self.handle_file_convert
```

### **4. Уведомления**
```python
class NotificationPlugin(PluginBase):
    def register_step_handlers(self, step_handlers):
        step_handlers["send_email"] = self.handle_send_email
        step_handlers["send_sms"] = self.handle_send_sms
        step_handlers["push_notification"] = self.handle_push_notification
```

---

## 📊 **МЕТРИКИ И МОНИТОРИНГ:**

### **Автоматический мониторинг:**
- ✅ Количество вызовов каждого типа шага
- ✅ Время выполнения
- ✅ Частота ошибок
- ✅ Результаты healthcheck

### **Логирование:**
```python
# В каждом обработчике
logger.info(f"🔄 {self.name}.{step_type}: Начало выполнения")
logger.debug(f"📝 {self.name}: Параметры: {params}")
logger.info(f"✅ {self.name}.{step_type}: Успешно завершен")
logger.error(f"❌ {self.name}.{step_type}: Ошибка: {error}")
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

## 🎯 **ROADMAP ПОДДЕРЖКИ НОВЫХ ПЛАГИНОВ:**

### **Этап 1: ✅ Текущий**
- Полная совместимость с HybridScenarioEngine
- Автоматические адаптеры через PluginCompatibilityEngine
- Руководство по созданию плагинов

### **Этап 2: 🔄 В разработке** 
- Автоматическая регистрация плагинов (plugin discovery)
- Валидация схемы параметров шагов  
- Автогенерация документации для типов шагов

### **Этап 3: 📋 Планируется**
- Web UI для создания плагинов
- Marketplace плагинов
- Версионирование и зависимости плагинов

---

## 📞 **ПОДДЕРЖКА РАЗРАБОТЧИКОВ:**

### **Документация:**
- 📖 `docs/NEW_PLUGIN_GUIDE.md` - это руководство
- 📋 `docs/scenario_format.md` - форматы сценариев
- 🏗️ `docs/MIGRATION_STRATEGY.md` - архитектурные изменения

### **Примеры:**
- 💡 `app/plugins/llm_plugin.py` - сложный плагин с конфигурацией
- 🔗 `app/plugins/telegram_plugin.py` - интеграция с внешним API
- 💾 `app/plugins/mongo_storage_plugin.py` - работа с базой данных

### **Тестирование:**
- 🧪 `test_simple_compatibility.py` - тест совместимости
- ✅ `tests/` - unit-тесты существующих плагинов

**Создавайте плагины, расширяйте систему! 🚀** 