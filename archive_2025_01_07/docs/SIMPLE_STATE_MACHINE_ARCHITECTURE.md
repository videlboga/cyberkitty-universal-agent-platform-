# 🔧 ПРОСТАЯ STATE MACHINE - АРХИТЕКТУРА

## 🎯 **ЦЕЛЬ:**
Заменить сложный ScenarioExecutor (871 строка) на простую, надежную систему

## 🏗️ **ОСНОВНЫЕ ПРИНЦИПЫ:**

### ✅ **ЧТО ДЕЛАЕМ:**
- **Один реестр состояний** вместо 3-х
- **Event-driven подход** без пауз/резюме  
- **Атомарные операции** - каждый шаг завершается мгновенно
- **Простые типы шагов** - только самое необходимое
- **Прозрачная отладка** - понятные логи

### ❌ **ЧТО УБИРАЕМ:**
- Сложную логику resume/pause
- Множественные флаги состояний  
- Циклические зависимости
- Магические строки
- Обработку ошибок в 5 местах

---

## 🔧 **ПРОСТАЯ АРХИТЕКТУРА:**

```python
# ===== ЯДРО СИСТЕМЫ =====
class SimpleScenarioEngine:
    def __init__(self):
        self.users_state: Dict[str, UserState] = {}  # user_id -> состояние
        self.handlers: Dict[str, Handler] = {}       # step_type -> обработчик
        self.scenarios: Dict[str, Scenario] = {}     # scenario_id -> сценарий
        
    async def process_event(self, user_id: str, event: Event) -> Response:
        """Единственная точка входа - обработать событие от пользователя"""
        user_state = self.get_or_create_user_state(user_id)
        current_step = self.get_current_step(user_state)
        
        # Простая логика: текущий шаг + событие = новое состояние
        result = await self.execute_step(current_step, event, user_state)
        
        if result.next_step:
            user_state.current_step = result.next_step
            
        return result.response

# ===== ТИПЫ ДАННЫХ =====
@dataclass
class UserState:
    user_id: str
    scenario_id: str
    current_step: str
    context: Dict[str, Any]
    created_at: datetime

@dataclass 
class Event:
    type: str           # "callback", "text", "start"
    data: Any           # callback_data, text, etc.
    telegram_data: Dict # chat_id, message_id, etc.

@dataclass
class StepResult:
    response: Optional[str]     # Ответ пользователю (может быть None)
    next_step: Optional[str]    # Следующий шаг (None = конец)
    update_context: Dict        # Обновления контекста

# ===== АТОМАРНЫЕ ШАГИ =====
class MenuStep(BaseStep):
    async def execute(self, event: Event, state: UserState) -> StepResult:
        if event.type != "callback":
            return StepResult(
                response="Выберите опцию из меню ⬇️",
                next_step=state.current_step  # Остаемся на том же шаге
            )
        
        choice = event.data
        next_step = self.config.get("choices", {}).get(choice)
        
        return StepResult(
            response=None,  # Не отвечаем, переходим к следующему шагу
            next_step=next_step,
            update_context={"last_choice": choice}
        )

class LLMStep(BaseStep):
    async def execute(self, event: Event, state: UserState) -> StepResult:
        # Вызываем LLM и сразу возвращаем результат
        llm_response = await self.call_llm(state.context.get("user_prompt"))
        
        return StepResult(
            response=f"🤖 **LLM ответ:**\n{llm_response}",
            next_step=self.config.get("next_step"),
            update_context={"last_llm_response": llm_response}
        )
```

---

## 🧩 **АТОМАРНЫЕ ШАБЛОНЫ:**

### **📁 Структура атомарных блоков:**
```
templates/atomic/
├── menu.yaml              # Простое меню с кнопками
├── text_input.yaml        # Ввод текста  
├── llm_request.yaml       # Запрос к LLM
├── confirmation.yaml      # Да/Нет
├── send_message.yaml      # Отправка сообщения
└── end.yaml              # Завершение
```

### **📝 Пример атомарного шаблона:**
```yaml
# templates/atomic/menu.yaml
atomic_template:
  type: "menu"
  name: "Простое меню"
  description: "Отображает кнопки и ждет выбор"
  
  config_schema:
    text: str           # Текст сообщения
    choices: Dict       # choice_id -> next_step  
    
  example:
    text: "Выберите действие:"
    choices:
      "test_llm": "llm_step"
      "test_rag": "rag_step"
      "exit": "end_step"
      
  generates_buttons: true
  expected_event_type: "callback"
```

---

## 🔄 **ПРОСТОЙ WORKFLOW:**

```python
# ===== ОБРАБОТКА СОБЫТИЙ =====
async def handle_telegram_callback(update, context):
    user_id = str(update.effective_user.id)
    callback_data = update.callback_query.data
    
    event = Event(
        type="callback",
        data=callback_data,
        telegram_data={
            "chat_id": update.effective_chat.id,
            "message_id": update.callback_query.message.message_id
        }
    )
    
    # ЕДИНСТВЕННЫЙ ВЫЗОВ
    response = await engine.process_event(user_id, event)
    
    if response:
        await send_telegram_message(event.telegram_data["chat_id"], response)

# ===== ПРОСТАЯ ЛОГИКА ВЫПОЛНЕНИЯ =====
async def execute_step(self, step_config: Dict, event: Event, state: UserState) -> StepResult:
    step_type = step_config["type"]
    handler = self.handlers.get(step_type)
    
    if not handler:
        return StepResult(
            response="❌ Ошибка: неизвестный тип шага",
            next_step="error_step"
        )
    
    try:
        result = await handler.execute(event, state, step_config)
        
        # Обновляем контекст
        if result.update_context:
            state.context.update(result.update_context)
            
        return result
        
    except Exception as e:
        logger.error(f"Ошибка выполнения шага {step_type}: {e}")
        return StepResult(
            response="❌ Произошла ошибка. Попробуйте позже.",
            next_step="error_step"
        )
```

---

## 📊 **СРАВНЕНИЕ:**

| **Аспект** | **Текущий ScenarioExecutor** | **Простая State Machine** |
|------------|------------------------------|---------------------------|
| **Строк кода** | 871 | ~200 |
| **Реестров состояний** | 3 | 1 |
| **Точек входа** | 5+ | 1 |
| **Типов ошибок** | 15+ | 3 |
| **Зависимостей** | Циклические | Линейные |
| **Отладка** | Сложная | Простая |
| **Тестирование** | Проблематичное | Легкое |

---

## 🚀 **ПЛАН МИГРАЦИИ:**

### **Этап 1: Параллельная реализация** (2-3 часа)
1. Создать `SimpleScenarioEngine` 
2. Реализовать базовые атомарные шаги
3. Создать простые тестовые сценарии

### **Этап 2: Тестирование** (1 час)  
1. Протестировать через Telegram
2. Сравнить с текущей системой
3. Исправить баги

### **Этап 3: Миграция** (1 час)
1. Переключить Telegram бот на новый engine
2. Мигрировать существующие сценарии
3. Удалить старый код

---

## 🎯 **РЕЗУЛЬТАТ:**
- ✅ **В 4 раза меньше кода** 
- ✅ **Простая отладка**
- ✅ **Надежная работа**
- ✅ **Легкое тестирование**
- ✅ **Быстрая разработка новых сценариев** 