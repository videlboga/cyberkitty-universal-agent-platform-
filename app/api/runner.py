from fastapi import APIRouter, HTTPException, status, Depends, Body
from app.db.agent_repository import AgentRepository, get_agent_repository
from app.db.scenario_repository import ScenarioRepository
from app.core.state_machine import ScenarioStateMachine
from app.core.scenario_executor import ScenarioExecutor, _resolve_value_from_context
from loguru import logger
from motor.motor_asyncio import AsyncIOMotorClient
import os
from typing import Optional, Dict, Any, Union
import json

# Добавляем новый импорт для функции-зависимости
from app.api.integration import get_scenario_executor_dependency

router = APIRouter(prefix="/agent-actions", tags=["runner"])

os.makedirs("logs", exist_ok=True)
logger.add("logs/agent_launch.log", format="{time} {level} {message}", level="INFO", rotation="10 MB", compression="zip", serialize=True)

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGODB_DATABASE_NAME = os.getenv("MONGODB_DATABASE_NAME", "universal_agent_platform")

client = AsyncIOMotorClient(MONGO_URI)
db = client[MONGODB_DATABASE_NAME]
agent_repo = AgentRepository(db)
scenario_repo = ScenarioRepository(db)

async def resolve_placeholders_in_response_recursively(data: Any, context: Dict[str, Any]) -> Any:
    """Рекурсивно разрешает плейсхолдеры в структуре данных (словарь или список)."""
    if isinstance(data, dict):
        return {k: await resolve_placeholders_in_response_recursively(v, context) for k, v in data.items()}
    elif isinstance(data, list):
        return [await resolve_placeholders_in_response_recursively(item, context) for item in data]
    elif isinstance(data, str):
        # Используем _resolve_value_from_context если он корректно обрабатывает и строки, и плейсхолдеры
        # или специфичную функцию для строк, если _resolve_value_from_context ожидает только плейсхолдеры вида {key}
        # В данном случае, _resolve_value_from_context должен подходить.
        return _resolve_value_from_context(data, context) # Убедимся, что эта функция async или вызываем её правильно
    return data

@router.post("/{agent_id}/run", status_code=status.HTTP_200_OK)
async def run_agent(
    agent_id: str, 
    input_data: Optional[Dict[str, Any]] = None,
    executor: ScenarioExecutor = Depends(get_scenario_executor_dependency)
):
    """
    Запустить сценарий агента (первый шаг) - подготавливает state machine.
    
    agent_id может быть ObjectId или строковым ID.
    """
    agent_repo_instance = AgentRepository(executor.db_session_for_direct_use) # Получаем репо с актуальной сессией
    scenario_repo_instance = ScenarioRepository(executor.db_session_for_direct_use)

    agent = await agent_repo_instance.get_by_id(agent_id)
    if not agent:
        logger.warning(f"Агент не найден: {agent_id}")
        raise HTTPException(status_code=404, detail=f"Agent not found: {agent_id}")
    
    scenario_id = agent.scenario_id
    if not scenario_id:
        logger.warning(f"У агента {agent_id} не назначен scenario_id.")
        raise HTTPException(status_code=400, detail=f"Agent {agent_id} has no scenario_id assigned.")
    
    scenario_model = await scenario_repo_instance.get_by_id(scenario_id)
    if not scenario_model:
        logger.warning(f"Сценарий не найден: {scenario_id}")
        raise HTTPException(status_code=404, detail=f"Scenario not found: {scenario_id}")
    
    sm_initial_context = scenario_model.initial_context.copy() if scenario_model.initial_context else {}
    if input_data:
        sm_initial_context.update(input_data)
    sm_initial_context["agent_id"] = agent.id # Используем agent.id, который должен быть строкой ObjectId
    sm_initial_context["__current_scenario_id__"] = scenario_id # Добавляем для ясности

    # Использование agent.settings для telegram_chat_id и user_id
    if agent.settings:
        agent_default_chat_id = agent.settings.get("default_telegram_chat_id")
        if agent_default_chat_id and not sm_initial_context.get("telegram_chat_id"):
            sm_initial_context["telegram_chat_id"] = agent_default_chat_id
            if not sm_initial_context.get("user_id"):
                 sm_initial_context["user_id"] = str(agent_default_chat_id)

    scenario_data_dict = scenario_model.model_dump(exclude_none=True)
    
    sm = ScenarioStateMachine(scenario_data_dict, sm_initial_context, executor)
    step_definition = sm.current_step()

    resolved_step = await resolve_placeholders_in_response_recursively(step_definition, sm.context)
    
    logger.info({
        "event": "agent_scenario_prepared", 
        "agent_id": agent.id, 
        "scenario_id": scenario_id, 
        "initial_payload_to_run_endpoint": input_data,
        "effective_sm_initial_context": sm.context, 
        "current_step_definition": resolved_step
    })
    return {
        "agent_id": agent.id, 
        "scenario_id": scenario_id, 
        "step": resolved_step, 
        "state": sm.serialize(), 
        "context": sm.context
    }

@router.post("/{agent_id}/step", status_code=status.HTTP_200_OK)
async def agent_next_step(
    agent_id: str, 
    input_data: Optional[Dict[str, Any]] = None, # input_data - это то, что пришло от пользователя (например, callback_data)
    state: Optional[Dict[str, Any]] = None,      # state - сериализованное состояние SM
    context: Optional[Dict[str, Any]] = None,   # context - предыдущий контекст SM
    executor: ScenarioExecutor = Depends(get_scenario_executor_dependency)
):
    """
    Обработать внешний ввод (например, callback_query от Telegram) и перейти к следующему шагу сценария.
    Этот эндпоинт обычно вызывается плагином (например, TelegramPlugin) после получения пользовательского ввода.
    """
    agent_repo_instance = AgentRepository(executor.db_session_for_direct_use)
    scenario_repo_instance = ScenarioRepository(executor.db_session_for_direct_use)

    agent = await agent_repo_instance.get_by_id(agent_id)
    if not agent:
        logger.warning(f"Агент не найден: {agent_id}")
        raise HTTPException(status_code=404, detail=f"Agent not found: {agent_id}")

    scenario_id_from_agent = agent.scenario_id
    # Если в контексте есть __current_scenario_id__, он может быть более актуален (например, для возобновления)
    scenario_id_from_context = context.get("__current_scenario_id__") if context else None
    final_scenario_id = scenario_id_from_context or scenario_id_from_agent

    if not final_scenario_id:
        logger.warning(f"Не удалось определить scenario_id для агента {agent.id}")
        raise HTTPException(status_code=400, detail=f"Cannot determine scenario_id for agent {agent.id}")

    scenario_model = await scenario_repo_instance.get_by_id(final_scenario_id)
    if not scenario_model:
        logger.warning(f"Сценарий '{final_scenario_id}' не найден.")
        raise HTTPException(status_code=404, detail=f"Scenario '{final_scenario_id}' not found.")

    if not state or not context:
        logger.warning(f"Для agent_next_step ({agent.id}) не предоставлены state или context.")
        raise HTTPException(status_code=400, detail="State and context are required to resume scenario execution.")
    
    # Инициализируем state machine из сохраненного состояния и контекста
    sm = ScenarioStateMachine.from_state(scenario_model.model_dump(exclude_none=True), state, context, executor)
    
    # Лог перед обработкой input_data и переходом
    logger.debug(f"[AGENT_NEXT_STEP AgentID:{agent.id}] SM loaded. Current step: {sm.current_step_index}. Input data: {input_data}")

    # Переходим к следующему шагу, используя input_data (например, callback_data)
    # sm.next_step() обработает input_data, обновит контекст и вернет определение СЛЕДУЮЩЕГО шага
    next_step_definition = sm.next_step(input_data) 

    # Теперь current_step() в sm указывает на шаг, к которому мы только что перешли
    current_step_after_input = sm.current_step()
    step_to_execute_or_return = current_step_after_input

    # Если текущий шаг после обработки ввода - это шаг, который должен быть выполнен executor'ом (action, llm_query и т.д.)
    if current_step_after_input and current_step_after_input.get("type") in ScenarioExecutor.AUTO_EXECUTABLE_STEP_TYPES:
        logger.info(f"[AGENT_NEXT_STEP AgentID:{agent.id}] Auto-executing step '{current_step_after_input.get('id')}' of type '{current_step_after_input.get('type')}'")
        try:
            # executor.execute_step модифицирует sm.context и может вернуть PAUSED_WAITING_FOR_CALLBACK
            execution_result_marker = await executor.execute_step(
                step_data=current_step_after_input, 
                state_machine=sm, 
                scenario_id_for_log=final_scenario_id
            )
            if execution_result_marker == "PAUSED_WAITING_FOR_CALLBACK":
                logger.info(f"[AGENT_NEXT_STEP AgentID:{agent.id}] Scenario paused by executor at step '{current_step_after_input.get('id')}'")
                # Возвращаем текущее состояние, так как сценарий на паузе
                step_to_execute_or_return = current_step_after_input 
            else:
                # Шаг был выполнен, переходим к следующему в SM
                next_step_definition_after_execution = sm.next_step() # Без input_data, т.к. это линейный переход
                step_to_execute_or_return = next_step_definition_after_execution

        except Exception as e:
            logger.error(f"[AGENT_NEXT_STEP AgentID:{agent.id}] Error auto-executing step '{current_step_after_input.get('id')}': {e}", exc_info=True)
            sm.context["__step_error__"] = f"Error executing step '{current_step_after_input.get('id')}': {str(e)}"
            # Если была ошибка, возвращаем текущий шаг (который вызвал ошибку) или null, если он не определен
            step_to_execute_or_return = current_step_after_input 
    
    resolved_step_to_return = await resolve_placeholders_in_response_recursively(step_to_execute_or_return, sm.context)

    logger.info({
        "event": "agent_step_processed", "agent_id": agent.id, "scenario_id": final_scenario_id,
        "input_data_received": input_data, 
        "final_sm_state": sm.serialize(), 
        "final_sm_context": sm.context, 
        "returned_step_definition": resolved_step_to_return
    })
    return {
        "agent_id": agent.id, 
        "scenario_id": final_scenario_id, 
        "step": resolved_step_to_return, 
        "state": sm.serialize(), 
        "context": sm.context
    }

@router.post("/{agent_id}/execute", status_code=status.HTTP_200_OK)
async def execute_scenario_endpoint(
    agent_id: str,
    payload: Optional[Dict[str, Any]] = Body(None),
    executor: ScenarioExecutor = Depends(get_scenario_executor_dependency),
    agent_repo: AgentRepository = Depends(get_agent_repository)
):
    """
    Выполнить сценарий полностью от начала до конца или до точки паузы (например, ожидание ввода).
    """
    logger.info(f"Запрос на выполнение сценария для агента {agent_id} через /execute. Payload: {payload}")
    
    agent_doc = await agent_repo.get_by_id(agent_id)
    if not agent_doc:
        logger.warning(f"Агент '{agent_id}' не найден.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Agent '{agent_id}' not found.")

    scenario_id_from_payload = payload.get("scenario_id") if payload else None
    final_scenario_id = scenario_id_from_payload or agent_doc.scenario_id

    if not final_scenario_id:
        logger.warning(f"Не удалось определить scenario_id для агента '{agent_doc.id}'. Payload: {payload}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Scenario ID not provided for agent '{agent_doc.id}' and not found in agent config.")

    logger.info(f"Запрос на полное выполнение сценария '{final_scenario_id}' для агента '{agent_doc.id}'.")
    scenario_model = await scenario_repo.get_by_id(final_scenario_id)
    if not scenario_model:
        logger.warning(f"Сценарий '{final_scenario_id}' не найден.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Scenario '{final_scenario_id}' not found.")

    initial_context_for_executor = {}
    if payload and isinstance(payload.get("context"), dict):
        initial_context_for_executor = payload["context"].copy()
        logger.info(f"Начальный контекст для executor загружен из payload['context'] для агента '{agent_doc.id}'.")
    
    # Добавляем agent_id, если его еще нет
    if "agent_id" not in initial_context_for_executor:
        initial_context_for_executor["agent_id"] = agent_doc.id
    if scenario_id_from_payload:
        initial_context_for_executor["__requested_scenario_id__"] = scenario_id_from_payload

    logger.debug(f"Подготовленный начальный контекст для ScenarioExecutor: {json.dumps(initial_context_for_executor, indent=2, default=str)} для агента '{agent_doc.id}', сценарий '{final_scenario_id}'")

    scenario_result: Optional[Dict[str, Any]] = None
    try:
        scenario_result = await executor.execute_scenario(
            scenario_doc=scenario_model.model_dump(exclude_none=True), 
            initial_context_from_runner=initial_context_for_executor,
            agent_id_from_runner=agent_doc.id 
        )
        logger.info(f"Сценарий '{final_scenario_id}' для агента '{agent_doc.id}' выполнен. Сообщение результата: {scenario_result.get('message') if scenario_result else 'N/A'}")

    except Exception as e:
        logger.error(f"Ошибка при выполнении сценария '{final_scenario_id}' для агента '{agent_doc.id}': {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error running scenario '{final_scenario_id}': {str(e)}")

    if scenario_result:
        cleaned_result = {}
        if isinstance(scenario_result, dict):
            # Ключи, которые точно нужно оставить, если они есть
            safe_keys = ["agent_id", "scenario_id", "success", "message", "error", "status", "scenario_instance_id"]
            # Ключи, которые могут содержать большие или циклические данные и требуют осторожности
            # (на данный момент просто копируем, но в будущем может понадобиться более глубокая очистка)
            potentially_large_keys = ["context", "state", "step", "final_context", "current_step_details"]

            for key, value in scenario_result.items():
                if key in safe_keys:
                    cleaned_result[key] = value
                elif key in potentially_large_keys:
                    # Для 'context' и подобных, которые могут быть большими, но обычно не циклическими в самой структуре JSON
                    # Здесь можно добавить более умную очистку, если проблема рекурсии сохранится.
                    # Например, ограничить глубину или размер.
                    # Пока просто копируем, предполагая, что execute_scenario уже вернул "безопасный" контекст.
                    cleaned_result[key] = value 
                elif key.startswith("__") and key.endswith("__"): # Пропускаем все системные переменные, если они не в safe_keys
                    continue 
                elif isinstance(value, ScenarioStateMachine): # Не сериализуем объект стейт-машины
                    continue
                else:
                     # Для неизвестных ключей, копируем, если они простые
                    if isinstance(value, (str, int, float, bool, list, dict, type(None))):
                        try:
                            # Простая проверка на сериализуемость в JSON, чтобы избежать сложных объектов
                            json.dumps(value, default=str) 
                            cleaned_result[key] = value
                        except (TypeError, OverflowError):
                            cleaned_result[key] = f"<unserializable_data_omitted type:{type(value).__name__}>"
                    else:
                        cleaned_result[key] = f"<complex_object_omitted type:{type(value).__name__}>"
            
            logger.info(f"Очищенный результат сценария для агента '{agent_doc.id}': {json.dumps(cleaned_result, indent=2, default=str, ensure_ascii=False)}")
            return cleaned_result
        else:
            logger.warning(f"Результат сценария для агента '{agent_doc.id}' не является словарем: {type(scenario_result)}. Возвращаем как есть.")
            return scenario_result
    else:
        logger.error(f"Executor сценария вернул None или пустой результат для агента '{agent_doc.id}', сценарий '{final_scenario_id}'")
        raise HTTPException(status_code=500, detail="Scenario execution returned no result.")