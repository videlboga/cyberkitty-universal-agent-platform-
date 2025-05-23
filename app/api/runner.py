from fastapi import APIRouter, HTTPException, status, Depends, Body
from app.db.agent_repository import AgentRepository, get_agent_repository
from app.db.scenario_repository import ScenarioRepository, get_scenario_repository
from app.core.state_machine import ScenarioStateMachine
from app.core.scenario_executor import ScenarioExecutor, _resolve_value_from_context
from loguru import logger
from typing import Optional, Dict, Any, Union
import json
import os

from app.api.integration import get_scenario_executor_dependency
from app.core.utils import resolve_string_template

router = APIRouter(prefix="/agent-actions", tags=["runner"])

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

# @router.post("/{agent_id}/run", status_code=status.HTTP_200_OK)
# async def run_agent(
#     agent_id: str, 
#     input_data: Optional[Dict[str, Any]] = Body(None),
#     executor: ScenarioExecutor = Depends(get_scenario_executor_dependency),
#     agent_repo: AgentRepository = Depends(get_agent_repository),
#     scenario_repo: ScenarioRepository = Depends(get_scenario_repository)
# ):
#     """
#     Запустить сценарий агента (первый шаг) - подготавливает state machine.
#     
#     agent_id может быть ObjectId или строковым ID.
#     """
#     agent = await agent_repo.get_by_id(agent_id)
#     if not agent:
#         logger.warning(f"Агент не найден: {agent_id}")
#         raise HTTPException(status_code=404, detail=f"Agent not found: {agent_id}")
#     
#     scenario_id = agent.scenario_id
#     if not scenario_id:
#         logger.warning(f"У агента {agent_id} не назначен scenario_id.")
#         raise HTTPException(status_code=400, detail=f"Agent {agent_id} has no scenario_id assigned.")
#     
#     scenario_model = await scenario_repo.get_by_id(scenario_id)
#     if not scenario_model:
#         logger.warning(f"Сценарий не найден: {scenario_id}")
#         raise HTTPException(status_code=404, detail=f"Scenario not found: {scenario_id}")
#     
#     sm_initial_context = scenario_model.initial_context.copy() if scenario_model.initial_context else {}
#     if input_data and "initial_context" in input_data and isinstance(input_data["initial_context"], dict):
#         sm_initial_context.update(input_data["initial_context"])
#         logger.info(f'Обновляем sm_initial_context из input_data["initial_context"]: {input_data["initial_context"]}')
#     elif input_data:
#         sm_initial_context.update(input_data)
#         logger.info(f'Обновляем sm_initial_context напрямую из input_data: {input_data}')
#
#     sm_initial_context["agent_id"] = agent.id
#     sm_initial_context["__current_scenario_id__"] = scenario_id
#
#     if agent.settings:
#         agent_default_chat_id = agent.settings.get("default_telegram_chat_id")
#         if agent_default_chat_id and not sm_initial_context.get("telegram_chat_id"):
#             sm_initial_context["telegram_chat_id"] = agent_default_chat_id
#             if not sm_initial_context.get("user_id"):
#                  sm_initial_context["user_id"] = str(agent_default_chat_id)
#
#     scenario_data_dict = scenario_model.model_dump(exclude_none=True)
#     
#     sm = ScenarioStateMachine(scenario_data_dict, sm_initial_context, executor)
#     step_definition = sm.current_step()
#
#     resolved_step = await resolve_placeholders_in_response_recursively(step_definition, sm.context)
#     
#     logger.info({
#         "event": "agent_scenario_prepared", 
#         "agent_id": agent.id, 
#         "scenario_id": scenario_id, 
#         "initial_payload_to_run_endpoint": input_data,
#         "effective_sm_initial_context": sm.context, 
#         "current_step_definition": resolved_step
#     })
#     return {
#         "agent_id": agent.id, 
#         "scenario_id": scenario_id, 
#         "step": resolved_step, 
#         "state": sm.serialize(), 
#         "context": sm.context
#     }

# @router.post("/{agent_id}/step", status_code=status.HTTP_200_OK)
# async def agent_next_step(
#     agent_id: str, 
#     input_data: Optional[Dict[str, Any]] = Body(None),
#     state: Optional[Dict[str, Any]] = Body(None),
#     context: Optional[Dict[str, Any]] = Body(None),
#     executor: ScenarioExecutor = Depends(get_scenario_executor_dependency),
#     agent_repo: AgentRepository = Depends(get_agent_repository),
#     scenario_repo: ScenarioRepository = Depends(get_scenario_repository)
# ):
#     """
#     Обработать внешний ввод (например, callback_query от Telegram) и перейти к следующему шагу сценария.
#     Этот эндпоинт обычно вызывается плагином (например, TelegramPlugin) после получения пользовательского ввода.
#     """
#     agent = await agent_repo.get_by_id(agent_id)
#     if not agent:
#         logger.warning(f"Агент не найден: {agent_id}")
#         raise HTTPException(status_code=404, detail=f"Agent not found: {agent_id}")
#
#     scenario_id_from_agent = agent.scenario_id
#     scenario_id_from_context = context.get("__current_scenario_id__") if context else None
#     final_scenario_id = scenario_id_from_context or scenario_id_from_agent
#
#     if not final_scenario_id:
#         logger.warning(f"Не удалось определить scenario_id для агента {agent.id}")
#         raise HTTPException(status_code=400, detail=f"Cannot determine scenario_id for agent {agent.id}")
#
#     scenario_model = await scenario_repo.get_by_id(final_scenario_id)
#     if not scenario_model:
#         logger.warning(f"Сценарий '{final_scenario_id}' не найден.")
#         raise HTTPException(status_code=404, detail=f"Scenario '{final_scenario_id}' not found.")
#
#     if not state or not context:
#         logger.warning(f"Для agent_next_step ({agent.id}) не предоставлены state или context.")
#         raise HTTPException(status_code=400, detail="State and context are required to resume scenario execution.")
#     
#     sm = ScenarioStateMachine.from_state(scenario_model.model_dump(exclude_none=True), state, context, executor)
#     
#     logger.debug(f"[AGENT_NEXT_STEP AgentID:{agent.id}] SM loaded. Current step: {sm.current_step_index}. Input data: {input_data}")
#
#     next_step_definition = await sm.async_next_step(input_data)
#
#     current_step_after_input = sm.current_step()
#     step_to_execute_or_return = current_step_after_input
#
#     if current_step_after_input and current_step_after_input.get("type") in ScenarioExecutor.AUTO_EXECUTABLE_STEP_TYPES:
#         logger.info(f"[AGENT_NEXT_STEP AgentID:{agent.id}] Auto-executing step '{current_step_after_input.get('id')}' of type '{current_step_after_input.get('type')}'")
#         try:
#             execution_result_marker = await executor.execute_step(
#                 step_data=current_step_after_input, 
#                 state_machine=sm, 
#                 scenario_id_for_log=final_scenario_id
#             )
#             if execution_result_marker == "PAUSED_WAITING_FOR_CALLBACK":
#                 logger.info(f"[AGENT_NEXT_STEP AgentID:{agent.id}] Scenario paused by executor at step '{current_step_after_input.get('id')}'")
#                 step_to_execute_or_return = current_step_after_input 
#             else:
#                 next_step_definition_after_execution = await sm.async_next_step()
#                 step_to_execute_or_return = next_step_definition_after_execution
#
#         except Exception as e:
#             logger.error(f"[AGENT_NEXT_STEP AgentID:{agent.id}] Error auto-executing step '{current_step_after_input.get('id')}': {e}", exc_info=True)
#             sm.context["__step_error__"] = f"Error executing step '{current_step_after_input.get('id')}': {str(e)}"
#             step_to_execute_or_return = current_step_after_input 
#     
#     resolved_step_to_return = await resolve_placeholders_in_response_recursively(step_to_execute_or_return, sm.context)
#
#     logger.info({
#         "event": "agent_step_processed", "agent_id": agent.id, "scenario_id": final_scenario_id,
#         "input_data_received": input_data, 
#         "final_sm_state": sm.serialize(), 
#         "final_sm_context": sm.context, 
#         "returned_step_definition": resolved_step_to_return
#     })
#     return {
#         "agent_id": agent.id, 
#         "scenario_id": final_scenario_id, 
#         "step": resolved_step_to_return, 
#         "state": sm.serialize(), 
#         "context": sm.context
#     }

@router.post("/{agent_id}/execute", status_code=status.HTTP_200_OK)
async def execute_scenario_endpoint(
    agent_id: str,
    payload: Optional[Dict[str, Any]] = Body(None),
    executor: ScenarioExecutor = Depends(get_scenario_executor_dependency),
    agent_repo: AgentRepository = Depends(get_agent_repository),
    scenario_repo: ScenarioRepository = Depends(get_scenario_repository)
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

    # Проверяем и добавляем user_id, если его нет, но есть user_telegram_id
    if "user_telegram_id" in initial_context_for_executor and "user_id" not in initial_context_for_executor:
        initial_context_for_executor["user_id"] = str(initial_context_for_executor["user_telegram_id"])
        logger.info(f"Runner Endpoint: Добавлен 'user_id': {initial_context_for_executor['user_id']} в контекст из 'user_telegram_id' для запуска агента {agent_doc.id}, сценарий {final_scenario_id}")
    elif "user_id" not in initial_context_for_executor:
        logger.warning(f"Runner Endpoint: 'user_id' отсутствует в initial_context_for_executor и не может быть получен из 'user_telegram_id'. Agent: {agent_doc.id}, Scenario: {final_scenario_id}. Контекст: {json.dumps(initial_context_for_executor, default=str)}")

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
        logger.info(f"[DEBUG] scenario_result type: {type(scenario_result)}, value: {json.dumps(scenario_result, default=str, ensure_ascii=False)}")
        cleaned_result = {}
        if isinstance(scenario_result, dict):
            # Ключи, которые точно нужно оставить, если они есть
            safe_keys = ["agent_id", "scenario_id", "success", "message", "error", "status", "scenario_instance_id"]
            # Ключи, которые могут конфликтовать с FastAPI/Starlette
            dangerous_keys = ["status", "headers", "body", "content", "cookies", "response", "request"]
            potentially_large_keys = ["context", "state", "step", "final_context", "current_step_details"]

            for key, value in scenario_result.items():
                if key in dangerous_keys:
                    logger.warning(f"[CLEANUP] Ключ '{key}' может конфликтовать с FastAPI. Переименовываю в 'result_{key}'.")
                    cleaned_result[f"result_{key}"] = value
                elif key in safe_keys:
                    cleaned_result[key] = value
                elif key in potentially_large_keys:
                    cleaned_result[key] = value
                elif key.startswith("__") and key.endswith("__"):
                    continue
                elif isinstance(value, (str, int, float, bool, list, dict, type(None))):
                    try:
                        json.dumps(value, default=str)
                        cleaned_result[key] = value
                    except (TypeError, OverflowError):
                        cleaned_result[key] = f"<unserializable_data_omitted type:{type(value).__name__}>"
                else:
                    cleaned_result[key] = f"<complex_object_omitted type:{type(value).__name__}>"
            logger.info(f"[DEBUG] cleaned_result type: {type(cleaned_result)}, value: {json.dumps(cleaned_result, default=str, ensure_ascii=False)}")
            return cleaned_result
        else:
            logger.warning(f"Результат сценария для агента '{agent_doc.id}' не является словарем: {type(scenario_result)}. Возвращаем как есть.")
            return scenario_result
    else:
        logger.error(f"Executor сценария вернул None или пустой результат для агента '{agent_doc.id}', сценарий '{final_scenario_id}'")
        raise HTTPException(status_code=500, detail="Scenario execution returned no result.")

@router.get("/test", status_code=200)
async def test_endpoint():
    """Тестовый endpoint для проверки инфраструктуры FastAPI."""
    return {"success": True, "message": "Test endpoint works!"}