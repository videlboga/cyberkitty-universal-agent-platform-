# Дневник ревизии Universal Agent Platform

## Дата начала: 2024-05-23

### 1. Обзор структуры проекта:
*   Проект использует Docker (`docker-compose.yml`) для оркестрации сервисов: `app` (FastAPI), `mongo` (MongoDB), `redis`. Заготовка для `frontend` присутствует, но закомментирована.
*   `README.md` содержит инструкции по запуску, примеры API (CRUD для User, Agent, Scenario; эндпоинты интеграций).
*   `DEVELOPMENT_PLAN.md` подробно описывает состояние проекта, MVP, текущие проблемы, планы и чек-листы. Отмечено, что E2E-тесты не реализованы (позже уточнено пользователем, что это "Пицца тест").

### 2. Анализ тестов:
*   В директории `tests/` находятся юнит- и интеграционные тесты, написанные с использованием `pytest` и `TestClient`.
*   Логирование тестов настроено через `loguru` в `logs/unit_tests.log`.
*   E2E тесты ("Пицца тест") существуют, но их расположение пока не определено.

### 3. Анализ моделей данных (Pydantic, находятся в `app/models/`):
*   **User**: `id` (`_id`), `name`, `email`, `created_at`, `extra`.
    *   `app/models/user.py`
*   **Agent**: `id` (`_id`), `name`, `scenario_id` (для связи со сценарием), `plugins`, `config`, `initial_context`, `created_at`, `extra`.
    *   `app/models/agent.py`
*   **Scenario**: `id` (`_id`), `scenario_id`, `name`, `description`, `version`, `initial_context`, `steps` (список шагов), `bpmn_xml` (помечен к удалению в `DEVELOPMENT_PLAN.md`), `created_at`, `extra`, `required_plugins`.
    *   `app/models/scenario.py`

### 4. E2E Тесты ("Пицца тест"):
*   Обнаружены JSON-файлы сценариев в директории `scenarios/`:
    *   `scenarios/test_pizza_poll.json`
    *   `scenarios/test_pizza_agent_hub.json`
    *   `scenarios/test_pizza_joke_delayed.json`
*   Анализ `scenarios/test_pizza_poll.json`:
    *   Содержит `scenario_id`, `name`, `description`, `initial_context` и список `steps`.
    *   Шаги включают: `telegram_send_message`, `input` (включая `callback_query`), `action` (для `update_context`), `llm_query`, `execute_sub_scenario`.
    *   Используются контекстные переменные (например, `{telegram_chat_id}`, `{user_id}`).
*   **Проблема**: Неясно, как эти JSON-сценарии используются для E2E тестирования. Отсутствует Python-код, который бы загружал, запускал и проверял эти сценарии.

### 5. Анализ выполнения сценариев и обработки ввода:
*   **Создание агента и сценария:**
    *   Сценарий создается через `POST /scenarios/` с JSON-телом.
    *   Агент создается через `POST /agents/` и может сразу получить `scenario_id` в теле запроса (согласно `app/api/agent.py`).
*   **Запуск сценария:**
    *   Первый шаг запускается через `POST /agent-actions/{agent_id}/run`.
    *   В `input_data` этого запроса можно передать начальные значения для контекста сценария.
    *   Ответ содержит первый шаг, `state` и `context`.
*   **Переход по шагам и имитация ввода:**
    *   Следующие шаги выполняются через `POST /agent-actions/{agent_id}/step`.
    *   В этот запрос передаются `state` и `context` из предыдущего ответа, а также `input_data` для текущего шага.
    *   `ScenarioStateMachine.next_step()` обновляет свой контекст данными из `input_data` запроса `/step`.
    *   Для шага `input` (например, ожидающего `callback_query` от Telegram), E2E тест должен передать в `input_data` эндпоинта `/step` словарь, где ключ - это `output_var` из шага `input`, а значение - имитируемый `callback_data` (например, `{"q1_callback_data": "q1_party"}`).
    *   Это позволит сценарию корректно обработать ввод и перейти к следующему шагу.
*   **Обработка шага `input` в `ScenarioExecutor.handle_input`:**
    *   Если `input_type: "callback_query"` и ввод еще не предоставлен, регистрируется ожидание в `self.waiting_for_input_events` и возвращается маркер `"PAUSED_WAITING_FOR_CALLBACK"`.
    *   **Важно:** Хотя `handle_input` возвращает `"PAUSED..."`, `ScenarioStateMachine.next_step()` все равно вызывается в `app/api/runner.py#agent_next_step`. `next_step` обновит контекст из `input_data` и попытается определить следующий шаг на основе этого обновленного контекста и логики `next_step_id` или `next_step_map` (если есть).
    *   Таким образом, E2E тест может "протолкнуть" данные для шага `input` через `input_data` эндпоинта `/step`, и `ScenarioStateMachine` подхватит их для определения дальнейшего хода сценария.

### 6. План E2E Тестирования (через `curl`):
*   **Подход**: Вместо Python-скриптов с `TestClient`, E2E тестирование будет проводиться с использованием последовательности `curl` команд, имитирующих реальные API-вызовы.
*   **Документирование**: Каждая `curl` команда, ее назначение, ожидаемый результат и фактический результат (предоставленный пользователем) будут документироваться в этом `AUDIT_LOG.md`.
*   **Сценарий для первого теста**: `test_pizza_poll.json` ("Пицца Опрос").

#### 6.1. E2E Тест: "Пицца Опрос" - Шаг 1: Создание сценария
*   **Команда `curl`:**
    ```bash
    # Заменить <API_URL> на актуальный URL API
    curl -X POST '<API_URL>/scenarios/' \
    -H "Content-Type: application/json" \
    -d @scenarios/test_pizza_poll.json
    ```
*   **Назначение**: Загружает JSON-описание сценария из файла `scenarios/test_pizza_poll.json` и создает новый сценарий в системе через API.
*   **Ожидаемый результат**:
    *   Статус код: `201 Created`.
    *   Тело ответа: JSON с данными созданного сценария, включая его уникальный `id`.
*   **Переменные для сохранения**: `SCENARIO_ID` (из поля `id` ответа).
*   **Дальнейшие действия**: Пользователь выполняет команду и предоставляет результаты (статус, `SCENARIO_ID`, ошибки).

#### 6.1.1. Результат Шага 1 (Создание сценария):
*   **Статус код**: `200 OK` (фактический, полученный от системы).
*   **SCENARIO_ID**: `682b32e753ac5e7f45cbe4cc` (из поля `_id` ответа).
*   **Ответ API (сокращенно)**:
    ```json
    {
      "_id": "682b32e753ac5e7f45cbe4cc",
      "scenario_id": "test_pizza_poll",
      "name": "Тест 'Какая ты пицца?'",
      // ... остальные поля ...
      "required_plugins": null
    }
    ```
*   **Замечания**: Сценарий успешно создан. Поле `id` в ответе называется `_id`. `required_plugins` в сценарии `null`.

#### 6.2. E2E Тест: "Пицца Опрос" - Шаг 2: Создание агента
*   **Необходимые данные**: `SCENARIO_ID` (полученный на Шаге 1: `682b32e753ac5e7f45cbe4cc`).
*   **Определение `required_plugins`**: Так как в сценарии `required_plugins` равно `null`, мы должны решить, какие плагины указать для агента. Исходя из типов шагов в `test_pizza_poll.json` (`telegram_send_message`, `input` с `callback_query`, `action` для `update_context`, `llm_query`), минимально необходимые плагины — это `TelegramPlugin` и `LLMPlugin`. Можно также добавить `MongoStoragePlugin`, если он используется для сохранения контекста между вызовами, но для одного прогона E2E-теста это может быть не критично.
    *   **Решение**: Используем `["TelegramPlugin", "LLMPlugin"]`.
*   **Команда `curl`:**
    ```bash
    # Заменить <API_URL> на актуальный URL API
    # Заменить <SCENARIO_ID> на ID, полученный на Шаге 1
    curl -X POST '<API_URL>/agents/' \
    -H "Content-Type: application/json" \
    -d '{
        "name": "E2E Pizza Poll Agent",
        "scenario_id": "<SCENARIO_ID>",
        "plugins": ["TelegramPlugin", "LLMPlugin"],
        "config": {},
        "initial_context": {}
    }'
    ```
*   **Назначение**: Создает нового агента, связывает его с созданным ранее сценарием и указывает необходимые плагины.
*   **Ожидаемый результат**:
    *   Статус код: `201 Created`.
    *   Тело ответа: JSON с данными созданного агента, включая его `id`.
*   **Переменные для сохранения**: `AGENT_ID` (из поля `id` ответа).
*   **Дальнейшие действия**: Пользователь выполняет команду и предоставляет результаты.

#### 6.2.1. Результат Шага 2 (Создание агента):
*   **Статус код**: `200 OK`.
*   **AGENT_ID**: `682d76f3b22809984b19d26f` (из поля `_id` ответа).
*   **Ответ API**:
    ```json
    {
      "_id": "682d76f3b22809984b19d26f",
      "name": "E2E Pizza Poll Agent",
      "scenario_id": "682b32e753ac5e7f45cbe4cc",
      "plugins": ["TelegramPlugin", "LLMPlugin"],
      "config": {},
      "initial_context": {},
      "created_at": "2025-05-21T06:47:15.163000",
      "extra": null
    }
    ```
*   **Замечания**: Агент успешно создан и связан со сценарием.

#### 6.3. E2E Тест: "Пицца Опрос" - Шаг 3: Запуск сценария (первый шаг)
*   **Необходимые данные**: `AGENT_ID` (полученный на Шаге 2: `682d76f3b22809984b19d26f`).
*   **Тестовые данные для инициализации контекста**: `TEST_USER_ID = "e2e_test_user_123"`, `TEST_CHAT_ID = "e2e_test_chat_456"`.
*   **Команда `curl`:**
    ```bash
    # Заменить <API_URL> на актуальный URL API
    # Заменить <AGENT_ID> на ID, полученный на Шаге 2
    curl -X POST '<API_URL>/agent-actions/<AGENT_ID>/run' \
    -H "Content-Type: application/json" \
    -d '{
        "telegram_chat_id": "e2e_test_chat_456",
        "user_id": "e2e_test_user_123"
    }'
    ```
*   **Назначение**: Запускает выполнение сценария, связанного с агентом. Передает начальные данные `telegram_chat_id` и `user_id` в контекст сценария.
*   **Ожидаемый результат**:
    *   Статус код: `200 OK`.
    *   Тело ответа: JSON, содержащий информацию о первом шаге сценария (`step`), текущее состояние (`state`) и контекст (`context`).
*   **Переменные для сохранения**: `CURRENT_STATE` (из поля `state` ответа), `CURRENT_CONTEXT` (из поля `context` ответа).
*   **Дальнейшие действия**: Пользователь выполняет команду и предоставляет результаты (статус, тело ответа, ошибки).

#### 6.3.1. Результат Шага 3 (Запуск сценария) - Попытка 1:
*   **Статус код**: `500 Internal Server Error`.
*   **Ответ API**: `Internal Server Error`.
*   **Анализ логов (`logs/errors.log` на тот момент)**:
    *   Обнаружена ключевая ошибка: `Шаг start_poll: TelegramPlugin не найден в ScenarioExecutor.`
    *   Это привело к тому, что `execute_step` вернул строку вместо ожидаемого dict, вызвав `execute_step вернул неожиданный тип: <class 'str'>`.
*   **Расследование проблемы с `TelegramPlugin`**:
    1.  **Проверка имен плагинов**: Имена классов `TelegramPlugin` и `LLMPlugin` в файлах плагинов (`app/plugins/`) совпадают с теми, что используются в коде.
    2.  **Анализ `ScenarioExecutor` (`app/core/scenario_executor.py`)**: `ScenarioExecutor` инициализируется с уже созданными экземплярами плагинов, переданными в конструктор. Он не загружает плагины динамически на основе конфигурации агента.
    3.  **Анализ `app/api/runner.py` и `app/api/integration.py`**: `ScenarioExecutor` инжектируется как зависимость `Depends(get_scenario_executor_dependency)`. Функция `get_scenario_executor_dependency` (`app/api/integration.py`) создает экземпляр `ScenarioExecutor`, передавая ему глобальные экземпляры плагинов.
    4.  **Анализ `app/core/dependencies.py`**: Глобальный экземпляр `telegram_plugin` инициализируется только если переменная окружения `TELEGRAM_BOT_TOKEN` задана. Если токен отсутствует, `telegram_plugin` остается `None`.
*   **Причина ошибки (предположительная на тот момент)**: Если `TELEGRAM_BOT_TOKEN` не установлен или недоступен для Docker-контейнера `app`, глобальный `telegram_plugin` будет `None`.
*   **Рекомендация**: Проверить и обеспечить корректную установку переменной окружения `TELEGRAM_BOT_TOKEN` в файле `.env` и перезапустить Docker-контейнеры.

#### 6.3.2. Результат Шага 3 (Запуск сценария) - Попытка 2 (после проверки `.env` и перезапуска Docker):
*   **Статус код**: `500 Internal Server Error`.
*   **Ответ API**: `Internal Server Error`.
*   **Анализ логов Docker-контейнера `app` (`docker logs universal_agent_system-app-1`)**:
    *   Новых ошибок, связанных с `TelegramPlugin не найден`, в `logs/errors.log` не появилось.
    *   Однако, в логах Docker-контейнера `app` обнаружена другая ключевая ошибка:
        ```
        Traceback (most recent call last):
          File "/app/app/api/runner.py", line 85, in run_agent  # Номер строки может отличаться в актуальной версии файла
            "state": sm.state,
                    ^^^^^^^^
        AttributeError: 'ScenarioStateMachine' object has no attribute 'state'
        ```
*   **Причина новой ошибки**: Код в `app/api/runner.py` (функция `run_agent`, а возможно и `agent_next_step`) пытается получить доступ к атрибуту `sm.state`, которого не существует у объекта `ScenarioStateMachine`.
*   **Анализ `app/core/state_machine.py`**:
    *   Состояние StateMachine (текущий шаг и т.д.) управляется через атрибут `self.current_step_index`.
    *   Присутствует метод `serialize()`, который возвращает словарь с ключевыми полями состояния:
        ```python
        def serialize(self) -> Dict[str, Any]:
            return {
                "current_step_index": self.current_step_index,
                "is_finished": self.is_finished,
                "error": self.error
            }
        ```
*   **Предложенное исправление для `AttributeError`**:
    *   В файле `app/api/runner.py`:
        *   В функции `run_agent`, в возвращаемом словаре заменить `"state": sm.state,` на `"state": sm.serialize(),`.
        *   В функции `agent_next_step`, в вызове `logger.info` и в возвращаемом словаре заменить `"state": sm.state,` на `"state": sm.serialize(),`.
*   **Статус**: Ожидается применение исправления для `AttributeError` в коде `app/api/runner.py`.

#### 6.3.3. Углубленный анализ и исправление управления состоянием (State Management):
*   **Проблема**: Первоначальный анализ показал, что `ScenarioStateMachine.serialize()` возвращал строку JSON, а не ожидаемый словарь. Кроме того, формат данных был неоптимален для восстановления.
    *   Старый `serialize()`: `json.dumps({"scenario": self.scenario_name, "state": {"step_index": self.current_step_index}, "context": self.context})`
    *   Это приводило бы к ошибкам в `app/api/runner.py` при попытке передать эту строку JSON как `state: dict` в `ScenarioStateMachine`.
*   **Решение (в `app/core/state_machine.py`)**:
    1.  Метод `serialize()` изменен для возврата словаря с ключевыми полями состояния:
        ```python
        def serialize(self) -> Dict[str, Any]:
            return {
                "current_step_index": self.current_step_index,
                "is_finished": self.is_finished,
                "error": self.error
            }
        ```
    2.  Добавлен метод `@classmethod from_state(cls, scenario_data, persisted_state, persisted_context, executor)` для корректной инициализации/восстановления `StateMachine` из этих частей.
    3.  Старый метод `from_json()` был удален, так как он не соответствовал новой логике.
*   **Решение (в `app/api/runner.py`)**:
    1.  В функции `run_agent`, инициализация `sm = ScenarioStateMachine(scenario_data_dict, sm_initial_context, executor)` остается корректной, так как `__init__` в `state_machine` ожидает `scenario_data` и `initial_context` (и `persisted_state` будет `None` через `from_state` в этом случае, если бы он вызывался).
    2.  В функции `agent_next_step`, вызов конструктора заменен на использование нового метода:
        `sm = ScenarioStateMachine.from_state(scenario.model_dump(), state, context, executor)`
        Здесь `state` и `context` приходят из тела запроса (`payload`) и соответствуют `persisted_state` и `persisted_context`.
*   **Статус**: Изменения в `app/core/state_machine.py` и `app/api/runner.py` применены. Ошибка `AttributeError` должна быть устранена, и управление состоянием должно работать корректнее.

#### 6.3.4. Результат Шага 3 (Запуск сценария) - Попытка 3 (после всех исправлений):
*   **Статус код**: `200 OK` (подразумевается, `curl` exit code 0).
*   **SCENARIO_ID**: `682b32e753ac5e7f45cbe4cc` (из ответа).
*   **AGENT_ID**: `682d76f3b22809984b19d26f` (из ответа).
*   **Ответ API**:
    ```json
    {
      "agent_id": "682d76f3b22809984b19d26f",
      "scenario_id": "682b32e753ac5e7f45cbe4cc",
      "step": {
        "id": "start_poll",
        "type": "telegram_send_message",
        "params": {
          "chat_id": "{telegram_chat_id}",
          "text": "Привет! Давай узнаем, какая ты пицца! Готов(а) ответить на несколько вопросов?",
          "inline_keyboard": [
            [
              {
                "text": "Да, поехали!",
                "callback_data": "pizza_poll_q1"
              }
            ]
          ]
        },
        "next_step_id": "wait_for_start_confirmation"
      },
      "state": {
        "current_step_index": 0,
        "is_finished": false,
        "error": null
      },
      "context": {
        "telegram_chat_id": "e2e_test_chat_456",
        "user_id": "e2e_test_user_123",
        "q1_answer": null,
        "q2_answer": null,
        "q3_answer": null,
        "pizza_poll_answers": {},
        "agent_id": "682d76f3b22809984b19d26f"
      }
    }
    ```
*   **Сохраненные переменные для следующего шага**:
    *   `CURRENT_STATE`: `{"current_step_index":0,"is_finished":false,"error":null}`
    *   `CURRENT_CONTEXT`: `{"telegram_chat_id":"e2e_test_chat_456","user_id":"e2e_test_user_123","q1_answer":null,"q2_answer":null,"q3_answer":null,"pizza_poll_answers":{},"agent_id":"682d76f3b22809984b19d26f"}`
*   **Замечания**: Сценарий успешно запущен! Ошибки `AttributeError` и проблемы с форматом состояния устранены. Система вернула первый шаг сценария и корректные `state` и `context`.

#### 6.4. E2E Тест: "Пицца Опрос" - Шаг 4: Передача callback_data для первого вопроса
*   **Необходимые данные**:
    *   `AGENT_ID`: `682d76f3b22809984b19d26f`
    *   `CURRENT_STATE` (из Шага 3): `{"current_step_index":0,"is_finished":false,"error":null}`
    *   `CURRENT_CONTEXT` (из Шага 3): `{"telegram_chat_id":"e2e_test_chat_456","user_id":"e2e_test_user_123","q1_answer":null,"q2_answer":null,"q3_answer":null,"pizza_poll_answers":{},"agent_id":"682d76f3b22809984b19d26f"}`
*   **Анализ сценария (`test_pizza_poll.json`)**:
    *   Первый шаг (`start_poll`) имеет `next_step_id: "wait_for_start_confirmation"`.
    *   Шаг `wait_for_start_confirmation` (тип `input`) ожидает `callback_query` "pizza_poll_q1" и сохраняет его в `output_var: "start_confirmation_cb"`.
*   **Команда `curl`:**
    ```bash
    curl -X POST 'http://localhost:8000/agent-actions/682d76f3b22809984b19d26f/step' \
    -H "Content-Type: application/json" \
    -d '{
        "state": {"current_step_index":0,"is_finished":false,"error":null},
        "context": {"telegram_chat_id":"e2e_test_chat_456","user_id":"e2e_test_user_123","q1_answer":null,"q2_answer":null,"q3_answer":null,"pizza_poll_answers":{},"agent_id":"682d76f3b22809984b19d26f"},
        "input_data": {
            "start_confirmation_cb": "pizza_poll_q1"
        }
    }'
    ```
*   **Назначение**: Имитирует нажатие пользователем кнопки "Да, поехали!" (`callback_data: "pizza_poll_q1"`).
*   **Ожидаемый результат**: 
        * Система обработает `input_data`, обновит контекст.
        * `ScenarioStateMachine` перейдет к шагу, указанному в `next_step_id` у `wait_for_start_confirmation` (это `ask_q1`).
        * API вернет описание шага `ask_q1`, обновленные `state` (с `current_step_index` указывающим на `ask_q1`) и `context`.

#### 6.4.1. Результат Шага 4 (Передача `callback_data` "pizza_poll_q1")
*   **Статус код**: `200 OK`.
*   **Ответ API**:
    ```json
    {
      "agent_id": "682d76f3b22809984b19d26f",
      "scenario_id": "682b32e753ac5e7f45cbe4cc",
      "step": {
        "id": "wait_for_start_confirmation",
        "type": "input",
        "params": {
          "prompt": "Невидимый шаг для ожидания callback_data от кнопки 'Да, поехали!'",
          "input_type": "callback_query",
          "expected_callback_data": "pizza_poll_q1",
          "output_var": "start_confirmation_cb"
        },
        "next_step_id": "ask_q1"
      },
      "state": {
        "current_step_index": 1,
        "is_finished": false,
        "error": null
      },
      "context": {
        "telegram_chat_id": "e2e_test_chat_456",
        "user_id": "e2e_test_user_123",
        "q1_answer": null,
        "q2_answer": null,
        "q3_answer": null,
        "pizza_poll_answers": {},
        "agent_id": "682d76f3b22809984b19d26f",
        "start_confirmation_cb": "pizza_poll_q1"
      }
    }
    ```
*   **Анализ ответа и логики `ScenarioStateMachine.next_step()`**:
    *   Входной `state` был `{"current_step_index":0,...}`.
    *   `ScenarioStateMachine.from_state()` устанавливает `self.current_step_index = 0`.
    *   `sm.next_step(input_data)`: 
        *   `step = self.current_step()` возвращает шаг `start_poll` (индекс 0).
        *   `input_data` (`start_confirmation_cb`) не относится к этому шагу, поэтому `next_step_map` не срабатывает.
        *   Переход происходит по `next_step_id` шага `start_poll`, который равен `wait_for_start_confirmation` (индекс 1).
        *   `self.current_step_index` обновляется на `1`.
        *   Метод `next_step()` возвращает описание шага `wait_for_start_confirmation`.
    *   Это объясняет, почему в ответе `step.id` это `wait_for_start_confirmation`, а `state.current_step_index` равен `1`.
    *   `input_data` (`{"start_confirmation_cb": "pizza_poll_q1"}`) было корректно добавлено в `context`.
*   **Сохраненные переменные для следующего шага**:
    *   `CURRENT_STATE`: `{"current_step_index":1,"is_finished":false,"error":null}`
    *   `CURRENT_CONTEXT`: `{"telegram_chat_id":"e2e_test_chat_456","user_id":"e2e_test_user_123","q1_answer":null,"q2_answer":null,"q3_answer":null,"pizza_poll_answers":{},"agent_id":"682d76f3b22809984b19d26f","start_confirmation_cb":"pizza_poll_q1"}`
*   **Замечания**: Шаг выполнен успешно. Система перешла на шаг `wait_for_start_confirmation` и сохранила `callback_data` в контексте. Следующий вызов `/step` должен обработать этот `callback_data` и перейти к `ask_q1`.

#### 6.5. E2E Тест: "Пицца Опрос" - Шаг 5: Обработка `callback_data` и переход к первому вопросу (`ask_q1`)
*   **Необходимые данные**:
    *   `AGENT_ID`: `682d76f3b22809984b19d26f`
    *   `CURRENT_STATE` (из Шага 4): `{"current_step_index":1,"is_finished":false,"error":null}` (указывает на `wait_for_start_confirmation`)
    *   `CURRENT_CONTEXT` (из Шага 4): `{"telegram_chat_id":"e2e_test_chat_456","user_id":"e2e_test_user_123",...,"start_confirmation_cb":"pizza_poll_q1"}`
*   **Команда `curl`:**
    ```bash
    curl -X POST 'http://localhost:8000/agent-actions/682d76f3b22809984b19d26f/step' \
    -H "Content-Type: application/json" \
    -d '{
        "state": {"current_step_index":1,"is_finished":false,"error":null},
        "context": {"telegram_chat_id":"e2e_test_chat_456","user_id":"e2e_test_user_123","q1_answer":null,"q2_answer":null,"q3_answer":null,"pizza_poll_answers":{},"agent_id":"682d76f3b22809984b19d26f","start_confirmation_cb":"pizza_poll_q1"},
        "input_data": {}
    }'
    ```
*   **Назначение**: `ScenarioStateMachine` должен использовать `start_confirmation_cb` из контекста для удовлетворения шага `wait_for_start_confirmation` и перейти к его `next_step_id` (`ask_q1`).
*   **Ожидаемый результат**: API вернет описание шага `ask_q1`, `state` с `current_step_index` указывающим на `ask_q1`.

#### 6.5.1. Результат Шага 5 (Переход к `ask_q1`)
*   **Статус код**: `200 OK`.
*   **Ответ API**:
    ```json
    {
      "agent_id": "682d76f3b22809984b19d26f",
      "scenario_id": "682b32e753ac5e7f45cbe4cc",
      "step": {
        "id": "ask_q1",
        "type": "telegram_send_message",
        "description": "Первый вопрос опросника",
        "params": {
          "chat_id": "{telegram_chat_id}",
          "text": "Вопрос 1: Какой твой идеальный вечер пятницы?",
          "inline_keyboard": [
            [{"text": "Шумная вечеринка с друзьями", "callback_data": "q1_party"}],
            [{"text": "Уютный вечер дома с книгой/фильмом", "callback_data": "q1_home"}],
            [{"text": "Активный отдых на природе", "callback_data": "q1_nature"}]
          ]
        },
        "next_step_id": "wait_q1_answer"
      },
      "state": {
        "current_step_index": 2,
        "is_finished": false,
        "error": null
      },
      "context": {
        "telegram_chat_id": "e2e_test_chat_456",
        "user_id": "e2e_test_user_123",
        "q1_answer": null,
        "q2_answer": null,
        "q3_answer": null,
        "pizza_poll_answers": {},
        "agent_id": "682d76f3b22809984b19d26f",
        "start_confirmation_cb": "pizza_poll_q1"
      }
    }
    ```
*   **Анализ ответа**:
    *   Система успешно перешла к шагу `ask_q1` (`current_step_index: 2`).
    *   В `step` ответа содержится описание шага `ask_q1`, включая его `inline_keyboard` с вариантами ответов (`q1_party`, `q1_home`, `q1_nature`).
*   **Сохраненные переменные для следующего шага**:
    *   `CURRENT_STATE`: `{"current_step_index":2,"is_finished":false,"error":null}`
    *   `CURRENT_CONTEXT`: `{"telegram_chat_id":"e2e_test_chat_456","user_id":"e2e_test_user_123","q1_answer":null,"q2_answer":null,"q3_answer":null,"pizza_poll_answers":{},"agent_id":"682d76f3b22809984b19d26f","start_confirmation_cb":"pizza_poll_q1"}`
*   **Замечания**: Все работает корректно. Следующий шаг – имитировать выбор пользователя для первого вопроса.

#### 6.6. E2E Тест: "Пицца Опрос" - Шаг 6: Передача ответа на первый вопрос ("q1_party")
*   **Необходимые данные**:
    *   `AGENT_ID`: `682d76f3b22809984b19d26f`
    *   `CURRENT_STATE` (из Шага 5.1): `{"current_step_index":3,"is_finished":false,"error":null}` (указывает на `wait_q1_answer`)
    *   `CURRENT_CONTEXT` (из Шага 5.1): `{"telegram_chat_id":"e2e_test_chat_456",...,"start_confirmation_cb":"pizza_poll_q1"}`
*   **Анализ сценария**:
    *   Шаг `ask_q1` (индекс 2) перешел на `wait_q1_answer` (индекс 3).
    *   Шаг `wait_q1_answer` (тип `input`) ожидает `callback_data` и сохранит его в `output_var: "q1_callback_data"`. Его `next_step_id` это `process_q1_answer`.
*   **Команда `curl` (Шаг 6.1 - переход к `wait_q1_answer`):**
    ```bash
    curl -X POST 'http://localhost:8000/agent-actions/682d76f3b22809984b19d26f/step' \
    -H "Content-Type: application/json" \
    -d '{"state": {"current_step_index":2,...}, "context": {...}, "input_data": {}}'
    ```
*   **Результат Шага 6.1 (Переход к `wait_q1_answer`)**:
    *   API вернул `step.id: "wait_q1_answer"`, `state.current_step_index: 3`.
*   **Команда `curl` (Шаг 6.2 - передача ответа `q1_party`):**
    ```bash
    curl -X POST 'http://localhost:8000/agent-actions/682d76f3b22809984b19d26f/step' \
    -H "Content-Type: application/json" \
    -d '{
        "state": {"current_step_index":3,"is_finished":false,"error":null},
        "context": {"telegram_chat_id":"e2e_test_chat_456",...,"start_confirmation_cb":"pizza_poll_q1"},
        "input_data": {"q1_callback_data": "q1_party"}
    }'
    ```
*   **Назначение**: Предоставить ответ на первый вопрос. `StateMachine` должен обновить контекст с `q1_callback_data` и перейти к шагу `process_q1_answer`.

#### 6.6.1. Результат Шага 6.2 (Передача ответа `q1_party`)
*   **Статус код**: `200 OK`.
*   **Ответ API**:
    ```json
    {
      "agent_id": "682d76f3b22809984b19d26f",
      "scenario_id": "682b32e753ac5e7f45cbe4cc",
      "step": {
        "id": "process_q1_answer",
        "type": "action",
        "params": {
          "action_type": "update_context",
          "updates": {
            "q1_answer": "{q1_callback_data}",
            "pizza_poll_answers.q1": "{q1_callback_data}"
          }
        },
        "next_step_id": "ask_q2"
      },
      "state": {
        "current_step_index": 4,
        "is_finished": false,
        "error": null
      },
      "context": {
        "telegram_chat_id": "e2e_test_chat_456",
        "user_id": "e2e_test_user_123",
        "q1_answer": null, 
        "q2_answer": null,
        "q3_answer": null,
        "pizza_poll_answers": {},
        "agent_id": "682d76f3b22809984b19d26f",
        "start_confirmation_cb": "pizza_poll_q1",
        "q1_callback_data": "q1_party"
      }
    }
    ```
*   **Анализ ответа и логики `runner.py`**:
    *   `StateMachine` корректно перешел к шагу `process_q1_answer` (`current_step_index: 4`).
    *   `input_data` ("q1_party") было добавлено в `context.q1_callback_data`.
    *   **Важно**: Поля `context.q1_answer` и `context.pizza_poll_answers.q1` еще НЕ обновлены в этом ответе. Это связано с тем, что шаг `process_q1_answer` (тип `action`, `action_type: update_context`) будет выполнен `ScenarioExecutor`-ом только при *следующем* вызове эндпоинта `/step`. Текущий ответ показывает состояние *перед* выполнением `action` шага `process_q1_answer`.
*   **Сохраненные переменные для следующего шага**:
    *   `CURRENT_STATE`: `{"current_step_index":4,"is_finished":false,"error":null}`
    *   `CURRENT_CONTEXT`: `{"telegram_chat_id":"e2e_test_chat_456","user_id":"e2e_test_user_123","q1_answer":null,"q2_answer":null,"q3_answer":null,"pizza_poll_answers":{},"agent_id":"682d76f3b22809984b19d26f","start_confirmation_cb":"pizza_poll_q1","q1_callback_data":"q1_party"}`
*   **Замечания**: Следующий вызов `/step` (с пустым `input_data`) должен выполнить `action` `process_q1_answer`, обновить контекст, а затем перейти к `ask_q2`.

### 7. Дальнейшие шаги (общие):
*   ~~Применить исправление для `AttributeError` в `app/api/runner.py`.~~ (Выполнено через `sed` и последующие правки `state_machine`)
*   **Перезапустить Docker-контейнеры, чтобы изменения вступили в силу.**
*   Повторно запустить Шаг 3 E2E теста (`curl` команду для `/agent-actions/{AGENT_ID}/run`).
*   Продолжить выполнение E2E теста "Пицца Опрос" шаг за шагом с использованием `curl`.
*   Проанализировать результаты каждого шага.
*   Выявить и задокументировать любые проблемы или несоответствия.
*   По итогам ревизии и тестирования, сформировать финальную документацию на основе этого `AUDIT_LOG.md`.
*   Продолжать документировать все эндпоинты, схемы и инструкции в `AUDIT_LOG.md`.
*   Проанализировать "Пицца тест" для понимания его структуры и проверяемых сценариев.
*   Выявить причины, по которым тесты не проходят.
*   Приступить к исправлению ошибок и доработке тестов/кода.
*   Дополнять этот дневник по мере продвижения. 