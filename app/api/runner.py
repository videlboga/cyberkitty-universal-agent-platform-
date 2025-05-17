from fastapi import APIRouter, HTTPException, status
from app.db.agent_repository import AgentRepository
from app.db.scenario_repository import ScenarioRepository
from app.core.state_machine import ScenarioStateMachine
from app.core.scenario_executor import ScenarioExecutor
from app.utils.id_helper import to_object_id, handle_id_query
from loguru import logger
from motor.motor_asyncio import AsyncIOMotorClient
import os
from typing import Optional, Dict, Any

router = APIRouter(prefix="/agent-actions", tags=["runner"])

os.makedirs("logs", exist_ok=True)
logger.add("logs/agent_launch.log", format="{time} {level} {message}", level="INFO", rotation="10 MB", compression="zip", serialize=True)

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/universal_agent")
client = AsyncIOMotorClient(MONGO_URI)
db = client.get_default_database()
agent_repo = AgentRepository(db)
scenario_repo = ScenarioRepository(db)

# Инициализируем исполнитель сценариев
scenario_executor = ScenarioExecutor(scenario_repo=scenario_repo, agent_repo=agent_repo)

@router.post("/{agent_id}/run", status_code=status.HTTP_200_OK)
async def run_agent(agent_id: str, input_data: dict = None):
    """
    Запустить сценарий агента (первый шаг)
    
    agent_id может быть ObjectId или именем агента, например "manager"
    """
    agent = await agent_repo.get_by_id(agent_id)
    if not agent:
        logger.warning(f"Агент не найден: {agent_id}")
        raise HTTPException(status_code=404, detail=f"Agent not found: {agent_id}")
    
    scenario_id = agent.scenario_id
    if not scenario_id:
        logger.warning(f"У агента {agent_id} не назначен scenario_id.")
        raise HTTPException(status_code=400, detail=f"Agent {agent_id} has no scenario_id assigned.")
    
    # Получаем сценарий по ID или имени
    scenario = await scenario_repo.get_by_id(scenario_id)
    if not scenario:
        logger.warning(f"Сценарий не найден: {scenario_id}")
        raise HTTPException(status_code=404, detail=f"Scenario not found: {scenario_id}")
    
    # Создаем начальный контекст с данными из input_data
    context = input_data or {}
    context["agent_id"] = agent_id
    
    # Получаем только первый шаг сценария
    sm = ScenarioStateMachine(scenario.model_dump())
    step = sm.current_step()
    
    logger.info({"event": "agent_launch", "agent_id": agent_id, "scenario_id": scenario_id, "step": step, "input": input_data})
    return {"agent_id": agent_id, "scenario_id": scenario_id, "step": step, "state": sm.state, "context": context}

@router.post("/{agent_id}/step", status_code=status.HTTP_200_OK)
async def agent_next_step(agent_id: str, input_data: dict = None, state: dict = None, context: dict = None):
    """
    Перейти к следующему шагу сценария агента
    
    agent_id может быть ObjectId или именем агента, например "manager"
    """
    agent = await agent_repo.get_by_id(agent_id)
    if not agent:
        logger.warning(f"Агент не найден: {agent_id}")
        raise HTTPException(status_code=404, detail=f"Agent not found: {agent_id}")
    
    scenario_id = agent.scenario_id
    if not scenario_id:
        logger.warning(f"У агента {agent_id} не назначен scenario_id.")
        raise HTTPException(status_code=400, detail=f"Agent {agent_id} has no scenario_id assigned.")
    
    # Получаем сценарий по ID или имени
    scenario = await scenario_repo.get_by_id(scenario_id)
    if not scenario:
        logger.warning(f"Сценарий не найден: {scenario_id}")
        raise HTTPException(status_code=404, detail=f"Scenario not found: {scenario_id}")
    
    # Инициализируем state machine с данными из запроса
    sm = ScenarioStateMachine(scenario.model_dump(), state, context)
    
    # Если тип текущего шага требует обработки через executor, обрабатываем его
    current_step = sm.current_step()
    if current_step:
        step_type = current_step.get("type")
        if step_type in scenario_executor.step_handlers:
            # Обрабатываем шаг через executor
            try:
                updated_context = await scenario_executor.execute_step(current_step, sm.context)
                # Обновляем контекст в state machine
                sm.context = updated_context
            except Exception as e:
                logger.error(f"Ошибка при обработке шага {step_type}: {e}")
    
    # Переходим к следующему шагу с обновленными данными
    next_step = sm.next_step(input_data)
    
    logger.info({"event": "agent_next_step", "agent_id": agent_id, "scenario_id": scenario_id, "input": input_data, "state": sm.state, "context": sm.context, "step": next_step})
    return {"agent_id": agent_id, "scenario_id": scenario_id, "step": next_step, "state": sm.state, "context": sm.context}

@router.post("/{agent_id}/execute", status_code=status.HTTP_200_OK)
async def execute_scenario(agent_id: str, payload: Optional[Dict[str, Any]] = None):
    """
    Выполнить сценарий полностью, обрабатывая все шаги последовательно
    
    agent_id может быть ObjectId или именем агента, например "manager"
    
    Args:
        agent_id: ID или имя агента
        payload: Тело запроса, ожидается {"context": {...начальный контекст...}}
        
    Returns:
        dict: Результат выполнения сценария (финальный контекст)
    """
    agent = await agent_repo.get_by_id(agent_id)
    if not agent:
        logger.warning(f"Агент не найден: {agent_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Agent not found: {agent_id}")
    
    scenario_id = agent.scenario_id
    if not scenario_id:
        logger.warning(f"У агента {agent_id} не назначен scenario_id.")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Agent {agent_id} has no scenario_id assigned.")
    
    scenario = await scenario_repo.get_by_id(scenario_id)
    if not scenario:
        logger.warning(f"Сценарий не найден: {scenario_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Scenario not found: {scenario_id}")
    
    # Извлекаем "полезный" контекст из тела запроса (payload)
    # и сразу инициализируем его, если он отсутствует или некорректен
    initial_context = {}
    if payload and "context" in payload and isinstance(payload.get("context"), dict):
        initial_context = payload["context"].copy() # Берем копию
    
    # Добавляем agent_id в этот "плоский" контекст
    initial_context["agent_id"] = agent_id
    
    logger.debug(f"Подготовленный начальный контекст для ScenarioExecutor: {initial_context} для агента {agent_id}")
    
    # Выполняем весь сценарий через executor
    try:
        # Передаем initial_context, который теперь "плоский"
        # Используем exclude_none=True для model_dump, чтобы не передавать None значения в ScenarioStateMachine
        result_context = await scenario_executor.execute_scenario(scenario.model_dump(exclude_none=True), initial_context)
        logger.info({"event": "scenario_executed", "agent_id": agent_id, "scenario_id": str(scenario.id), "success": True})
        # result_context, возвращаемый ScenarioExecutor'ом, уже должен быть "плоским"
        return {"agent_id": agent_id, "scenario_id": str(scenario.id), "success": True, "context": result_context}
    except Exception as e:
        logger.error({"event": "scenario_execution_error", "agent_id": agent_id, "scenario_id": str(scenario.id), "error": str(e)})
        # Добавляем exception=True для полного трейсбека в логах, если это необходимо
        logger.exception(f"Ошибка при выполнении сценария {scenario_id} для агента {agent_id}") 
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error executing scenario: {str(e)}") 