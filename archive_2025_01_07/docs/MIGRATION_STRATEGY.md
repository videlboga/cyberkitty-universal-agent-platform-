# 🚀 СТРАТЕГИЯ ПОСТЕПЕННОЙ МИГРАЦИИ

## 🎯 **ЦЕЛЬ:**
Перейти к простой и надежной системе **БЕЗ** нарушения работы существующих компонентов

---

## 📊 **ТЕКУЩЕЕ СОСТОЯНИЕ СИСТЕМЫ:**

### ✅ **ЧТО РАБОТАЕТ:**
- **8 плагинов** с обработчиками: TelegramPlugin, LLMPlugin, RAGPlugin, MongoStoragePlugin, OrchestratorPlugin, SchedulerPlugin, SchedulingPlugin  
- **22+ типа шагов**: `telegram_send_message`, `llm_query`, `rag_search`, `mongo_insert_one`, etc.
- **Формат JSON сценариев** с массивом шагов
- **Интерфейс плагинов**: `register_step_handlers(Dict[str, Callable])`
- **Template substitution**: `{variable}` в тексте

### ❌ **ЧТО НЕ РАБОТАЕТ:**
- **Сложная логика пауз/резюме** в ScenarioExecutor (871 строка)
- **Множественные реестры состояний** (3 штуки)
- **Callback обработка** (разные реестры для регистрации и поиска) 
- **Нестабильные input шаги**

---

## 🛣️ **ПЛАН МИГРАЦИИ (4 ЭТАПА):**

### **ЭТАП 1: СОЗДАНИЕ АДАПТЕРОВ (2 часа)**
**Цель:** Полная совместимость без изменений в плагинах

```python
# ===== НОВЫЙ ФАЙЛ: app/core/migration_engine.py =====

class MigrationEngine:
    \"\"\"Движок с поддержкой старого и нового API одновременно\"\"\"
    
    def __init__(self, plugins: list):
        # Старый интерфейс (ScenarioExecutor compatibility)
        self.scenario_executor = HybridScenarioEngine(plugins)
        
        # Новый интерфейс (SimpleScenarioEngine) 
        self.simple_engine = SimpleScenarioEngine()
        
        # Адаптеры плагинов
        self.plugin_adapter = PluginCompatibilityEngine(plugins)
        
        # Флаг режима работы
        self.mode = "hybrid"  # "legacy", "hybrid", "simple"
    
    async def execute_scenario(self, scenario_data: Dict, context: Dict = None) -> Dict:
        \"\"\"УНИВЕРСАЛЬНЫЙ МЕТОД - работает с любым форматом\"\"\"
        if self.mode == "legacy":
            return await self._execute_legacy(scenario_data, context)
        elif self.mode == "simple":
            return await self._execute_simple(scenario_data, context)
        else:  # hybrid
            return await self._execute_hybrid(scenario_data, context)
    
    async def _execute_hybrid(self, scenario_data: Dict, context: Dict) -> Dict:
        \"\"\"Гибридное выполнение - пробует простое, откатывается к старому\"\"\"
        try:
            # Пробуем простую систему
            if self._is_simple_compatible(scenario_data):
                return await self.simple_engine.execute_scenario_dict(scenario_data, context)
            else:
                # Откатываемся к совместимому режиму
                return await self.scenario_executor.execute_scenario_dict(scenario_data, context)
        except Exception as e:
            logger.error(f\"Ошибка в гибридном режиме: {e}\")
            # Последний шанс - legacy режим
            return await self.scenario_executor.execute_scenario_dict(scenario_data, context)
```

**✅ Результат этапа:**
- Все плагины работают как раньше
- Появляется возможность использовать простые сценарии
- Zero breaking changes

---

### **ЭТАП 2: СОЗДАНИЕ АТОМАРНЫХ ШАБЛОНОВ (3 часа)**
**Цель:** Библиотека надежных блоков для новых сценариев

```yaml
# ===== templates/atomic/ =====
menu.yaml              # ✅ Готов - простое меню с кнопками
llm_request.yaml        # ✅ Готов - запрос к LLM  
text_input.yaml         # ⏳ TODO - ввод текста
confirmation.yaml       # ⏳ TODO - Да/Нет
send_message.yaml       # ⏳ TODO - отправка сообщения
rag_search.yaml         # ⏳ TODO - поиск в RAG
mongo_operation.yaml    # ⏳ TODO - работа с MongoDB
scheduler_delay.yaml    # ⏳ TODO - отложенное выполнение
```

**✅ Результат этапа:**
- 8+ атомарных шаблонов с unit-тестами
- Конструктор сценариев из атомарных блоков
- Документация использования

---

### **ЭТАП 3: МЯГКАЯ ИНТЕГРАЦИЯ (2 часа)**
**Цель:** Добавить простые сценарии в систему без замены существующих

```python
# ===== app/core/unified_executor.py =====

class UnifiedExecutor:
    \"\"\"Объединенная система - поддерживает оба типа сценариев\"\"\"
    
    def __init__(self, plugins: list):
        self.migration_engine = MigrationEngine(plugins)
        
    async def run_scenario(self, scenario_id: str, scenario_type: str = "auto") -> Dict:
        \"\"\"
        scenario_type:
        - "auto": автоопределение формата
        - "legacy": принудительно старый формат  
        - "simple": принудительно новый формат
        \"\"\"
        
        scenario_data = await self.load_scenario(scenario_id)
        
        if scenario_type == "auto":
            # Автоопределение по структуре
            if self._is_legacy_format(scenario_data):
                return await self.migration_engine.execute_scenario(scenario_data)
            else:
                return await self.migration_engine.execute_scenario(scenario_data)
        else:
            self.migration_engine.mode = scenario_type
            return await self.migration_engine.execute_scenario(scenario_data)
```

**✅ Результат этапа:**
- Поддержка старых JSON сценариев (100% совместимость)
- Поддержка новых простых сценариев
- Автоматический выбор движка по формату

---

### **ЭТАП 4: ОПЦИОНАЛЬНАЯ ЗАМЕНА (1 час)**
**Цель:** Возможность полного перехода на простую систему

```python
# ===== config/migration_config.yaml =====
migration:
  mode: "hybrid"                    # "legacy", "hybrid", "simple"
  deprecated_step_types:            # Шаги, которые больше не поддерживаются
    - "input"                       # Заменен на simple_menu
    - "complex_branch"              # Заменен на простую логику
  
  compatibility_warnings: true     # Предупреждения о deprecated
  
  fallback_strategy: "legacy"      # Что делать при ошибках: "legacy", "error"
```

**✅ Результат этапа:**
- Конфигурируемая миграция
- Возможность отключить старые компоненты
- Метрики использования для принятия решений

---

## 📊 **СОВМЕСТИМОСТЬ ПЛАГИНОВ:**

### **🔌 ПЛАГИНЫ С ПОЛНОЙ СОВМЕСТИМОСТЬЮ:**
- ✅ **TelegramPlugin**: `telegram_send_message`, `telegram_edit_message`  
- ✅ **LLMPlugin**: `llm_query`
- ✅ **RAGPlugin**: `rag_search`
- ✅ **MongoStoragePlugin**: `mongo_insert_one`, `mongo_find_one`, `mongo_update_one`, `mongo_delete_one`
- ✅ **OrchestratorPlugin**: `execute_scenario`, `execute_scenarios_parallel`, `execute_scenarios_sequence`, `conditional_execute`
- ✅ **SchedulerPlugin**: `schedule_delay`, `schedule_at`, `schedule_periodic`, `cancel_schedule`
- ✅ **SchedulingPlugin**: `schedule_scenario_run`

### **📝 ИНТЕРФЕЙС АДАПТЕРА:**

```python
# Старый обработчик плагина остается без изменений:
async def handle_llm_query(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
    # Существующий код плагина - НИКАКИХ ИЗМЕНЕНИЙ!
    pass

# Адаптер автоматически интегрирует его в простую систему:
class LLMAdapter(BaseStep):
    async def execute(self, event: Event, state: UserState) -> StepResult:
        # Превращает Event/UserState в step_data/context
        # Вызывает старый handle_llm_query
        # Превращает результат обратно в StepResult
        pass
```

---

## 🚦 **КОНТРОЛЬНЫЕ ТОЧКИ:**

### **КОНТРОЛЬНАЯ ТОЧКА 1** (после этапа 1):
- [ ] Все существующие плагины работают
- [ ] Все существующие сценарии выполняются
- [ ] Новый HybridScenarioEngine проходит unit-тесты
- [ ] PluginCompatibilityEngine показывает 100% совместимость

### **КОНТРОЛЬНАЯ ТОЧКА 2** (после этапа 2):  
- [ ] 8+ атомарных шаблонов работают
- [ ] Конструктор сценариев создает валидные сценарии
- [ ] Unit-тесты покрывают >90% атомарных блоков

### **КОНТРОЛЬНАЯ ТОЧКА 3** (после этапа 3):
- [ ] UnifiedExecutor работает с обоими форматами
- [ ] Автоопределение формата работает корректно
- [ ] Telegram бот работает с новыми простыми сценариями

### **КОНТРОЛЬНАЯ ТОЧКА 4** (после этапа 4):
- [ ] Конфигурируемая миграция работает
- [ ] Метрики показывают стабильность системы
- [ ] Возможность отключения legacy компонентов

---

## 🎯 **КРИТЕРИИ УСПЕХА:**

### **ТЕХНИЧЕСКИЕ:**
- ✅ **0 breaking changes** для существующих плагинов
- ✅ **100% совместимость** со старыми сценариями  
- ✅ **<200 строк кода** для простого engine
- ✅ **<30 секунд** время выполнения типового сценария
- ✅ **>95% uptime** Telegram бота после миграции

### **БИЗНЕС:**
- ✅ **В 5 раз быстрее** создание новых сценариев
- ✅ **В 10 раз проще** отладка проблем
- ✅ **100% покрытие** unit-тестами атомарных блоков
- ✅ **Zero downtime** при миграции

---

## 🛡️ **ПЛАН ОТКАТА:**

Если что-то пойдет не так на любом этапе:

1. **Откат конфигурации**: `migration.mode = "legacy"`
2. **Удаление новых файлов**: Все новые файлы - опциональные
3. **Восстановление ScenarioExecutor**: Исходный код сохранен
4. **Rollback git**: Каждый этап - отдельный commit

**⏱️ Время отката: < 5 минут**

---

## 📈 **ПЛАНИРУЕМЫЕ РЕЗУЛЬТАТЫ:**

### **ПОСЛЕ ЗАВЕРШЕНИЯ МИГРАЦИИ:**

- 🚀 **Стабильная система** с простой архитектурой
- 🔌 **Все плагины работают** через адаптеры  
- ⚡ **Быстрая разработка** новых сценариев
- 🛡️ **Легкая отладка** и мониторинг
- 📊 **Гибкий выбор** между простыми и сложными сценариями
- 🔄 **Обратная совместимость** со всем существующим кодом 