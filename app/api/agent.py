import os
from fastapi import APIRouter, HTTPException, status, Body, Depends
from app.models.agent import Agent
from app.models.scenario import Scenario
from app.db.agent_repository import AgentRepository, get_agent_repository
from app.db.scenario_repository import ScenarioRepository, get_scenario_repository
from loguru import logger
from typing import List, Optional, Dict, Any, Tuple
from pydantic import BaseModel

# Модель для запроса на обновление агента
class AgentUpdateRequest(BaseModel):
    name: Optional[str] = None
    scenario_id: Optional[str] = None
    plugins: Optional[List[str]] = None
    config: Optional[Dict[str, Any]] = None
    extra: Optional[Dict[str, Any]] = None

router = APIRouter(prefix="/agents", tags=["agents"])

async def check_agent_scenario_compatibility(agent_data: Agent | AgentUpdateRequest, scenario_data: Scenario) -> Tuple[bool, Optional[str]]: # Возвращаем также сообщение об ошибке
    # В реальной реализации здесь будет проверка, например, по agent_data.plugins и scenario_data.required_plugins
    logger.debug(f"Проверка совместимости для агента (plugins: {getattr(agent_data, 'plugins', [])}) и сценария {scenario_data.id} (required: {getattr(scenario_data, 'required_plugins', [])})")
    
    # Получаем плагины агента. Учитываем, что agent_data может быть Agent или AgentUpdateRequest
    # и поле plugins может быть None или отсутствовать в AgentUpdateRequest, если не передано.
    agent_plugins = []
    if hasattr(agent_data, 'plugins') and agent_data.plugins is not None:
        agent_plugins = agent_data.plugins
    elif isinstance(agent_data, AgentUpdateRequest) and agent_data.config and "plugins" in agent_data.config:
        # Фоллбэк на config, если вдруг используется старый формат передачи плагинов в апдейте (маловероятно после наших правок)
        # Это можно будет убрать, когда будем уверены, что plugins всегда передаются через поле верхнего уровня
        if isinstance(agent_data.config["plugins"], list):
             agent_plugins = agent_data.config["plugins"]

    required_plugins = scenario_data.required_plugins if scenario_data.required_plugins is not None else []

    if not required_plugins: # Если сценарию не нужны плагины, он совместим с любым агентом
        return True, None

    missing_plugins = [p for p in required_plugins if p not in agent_plugins]
    
    if missing_plugins:
        error_message = f"Agent is missing required plugins: {', '.join(missing_plugins)}"
        logger.warning(f"Агент несовместим со сценарием {scenario_data.id}: {error_message}")
        return False, error_message
        
    return True, None

@router.post("/", response_model=Agent, status_code=status.HTTP_201_CREATED)
async def create_agent(
    agent_payload: Agent,
    agent_repo: AgentRepository = Depends(get_agent_repository),
    scenario_repo: ScenarioRepository = Depends(get_scenario_repository)
):
    # Добавляем логику для default_telegram_chat_id
    # Pydantic v2 с extra='allow' должен сделать 'settings' доступным как атрибут,
    # если он был в JSON-запросе.
    
    chat_id_found_in_payload = False
    # Сначала проверяем, существует ли атрибут 'settings' и является ли он словарем
    if hasattr(agent_payload, 'settings') and agent_payload.settings is not None and isinstance(agent_payload.settings, dict):
        if agent_payload.settings.get("default_telegram_chat_id"):
            chat_id_found_in_payload = True
            logger.info(f"default_telegram_chat_id '{agent_payload.settings.get('default_telegram_chat_id')}' найден в payload агента.")
    else:
        # Если атрибута 'settings' нет или он None, логируем это.
        logger.info("Атрибут 'settings' отсутствует или None в agent_payload перед проверкой ENV.")

    if not chat_id_found_in_payload:
        logger.info("default_telegram_chat_id не найден в payload или отсутствует, пытаемся загрузить из ENV TEST_TELEGRAM_CHAT_ID.")
        env_chat_id = os.getenv("TEST_TELEGRAM_CHAT_ID")
        if env_chat_id:
            logger.info(f"TEST_TELEGRAM_CHAT_ID из ENV: '{env_chat_id}'. Добавляем/обновляем в agent_payload.settings.")
            # Если settings не существует как атрибут, или не словарь, создаем его
            # Важно: Pydantic v2 при extra='allow' создаст атрибут, если ему присвоить значение.
            # Но если он уже есть и не dict, это проблема. Лучше явно создать, если его нет.
            if not hasattr(agent_payload, 'settings') or not isinstance(getattr(agent_payload, 'settings', None), dict):
                logger.info("Создаем атрибут 'settings' в agent_payload как пустой dict.")
                agent_payload.settings = {} 
            
            # Теперь agent_payload.settings точно существует и является словарем
            agent_payload.settings["default_telegram_chat_id"] = env_chat_id
            logger.info(f"agent_payload.settings после обновления из ENV: {agent_payload.settings}")
        else:
            logger.warning("TEST_TELEGRAM_CHAT_ID не найден в ENV. default_telegram_chat_id не будет установлен автоматически.")

    if agent_payload.scenario_id:
        scenario = await scenario_repo.get_by_id(agent_payload.scenario_id)
        if not scenario:
            logger.warning(f"Попытка создать агента с несуществующим scenario_id: {agent_payload.scenario_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Scenario with id '{agent_payload.scenario_id}' not found."
            )
        
        compatible, error_msg = await check_agent_scenario_compatibility(agent_payload, scenario)
        if not compatible:
            logger.warning(f"Агент несовместим со сценарием {agent_payload.scenario_id}: {error_msg}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, 
                detail=error_msg or f"Agent is not compatible with scenario '{agent_payload.scenario_id}'."
            )

    created_agent = await agent_repo.create(agent_payload)
    # Добавим лог, чтобы увидеть, что сохранилось в settings
    saved_settings = None
    if hasattr(created_agent, 'settings') and created_agent.settings is not None:
        saved_settings = created_agent.settings
    logger.info(f"Агент создан: {created_agent.name} с ID {created_agent.id}. Сохраненные settings: {saved_settings}")
    return created_agent

@router.get("/", response_model=List[Agent])
async def list_agents(
    skip: int = 0, 
    limit: int = 100,
    agent_repo: AgentRepository = Depends(get_agent_repository)
):
    agents = await agent_repo.get(skip=skip, limit=limit)
    logger.info(f"Запрошен список агентов: {len(agents)} найдено")
    return agents

@router.get("/{agent_id}", response_model=Agent)
async def get_agent(
    agent_id: str,
    agent_repo: AgentRepository = Depends(get_agent_repository)
):
    agent = await agent_repo.get_by_id(agent_id)
    if not agent:
        logger.warning(f"Агент не найден: {agent_id}")
        raise HTTPException(status_code=404, detail="Agent not found")
    logger.info(f"Агент найден: {agent_id}")
    return agent

@router.patch("/{agent_id}", response_model=Agent)
async def update_agent(
    agent_id: str, 
    agent_update_payload: AgentUpdateRequest = Body(...),
    agent_repo: AgentRepository = Depends(get_agent_repository),
    scenario_repo: ScenarioRepository = Depends(get_scenario_repository)
):
    existing_agent = await agent_repo.get_by_id(agent_id)
    if not existing_agent:
        logger.warning(f"Агент не найден для обновления: {agent_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")

    update_data = agent_update_payload.model_dump(exclude_unset=True)
    
    # Если сценарий обновляется, нужно проверить совместимость
    # Для этого нам нужна "финальная" версия данных агента после предполагаемого обновления
    # Создадим временную копию существующего агента и применим к ней изменения из agent_update_payload
    # Это важно, так как agent.plugins могли измениться в этом же запросе
    potential_agent_state = existing_agent.copy(deep=True) 
    if agent_update_payload.name is not None: potential_agent_state.name = agent_update_payload.name
    if agent_update_payload.scenario_id is not None: potential_agent_state.scenario_id = agent_update_payload.scenario_id
    if agent_update_payload.plugins is not None: potential_agent_state.plugins = agent_update_payload.plugins
    if agent_update_payload.config is not None: potential_agent_state.config = {**(potential_agent_state.config or {}), **agent_update_payload.config}
    if agent_update_payload.extra is not None: potential_agent_state.extra = {**(potential_agent_state.extra or {}), **agent_update_payload.extra}


    if "scenario_id" in update_data and update_data["scenario_id"] != existing_agent.scenario_id:
        new_scenario_id = update_data["scenario_id"]
        if new_scenario_id is not None: 
            scenario = await scenario_repo.get_by_id(new_scenario_id)
            if not scenario:
                logger.warning(f"Попытка обновить агента {agent_id} несуществующим scenario_id: {new_scenario_id}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Scenario with id '{new_scenario_id}' not found."
                )
            
            compatible, error_msg = await check_agent_scenario_compatibility(potential_agent_state, scenario)
            if not compatible:
                logger.warning(f"Агент {agent_id} несовместим с новым сценарием {new_scenario_id}: {error_msg}")
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT, 
                    detail=error_msg or f"Agent is not compatible with scenario '{new_scenario_id}'."
                )
        # Если new_scenario_id is None, значит мы отвязываем сценарий, это допустимо

    if not update_data: # Если нечего обновлять
        return existing_agent
        
    updated_agent = await agent_repo.update(agent_id, update_data)
    if not updated_agent: # На случай, если update в репозитории может вернуть None
        logger.error(f"Ошибка при обновлении агента {agent_id} в репозитории")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update agent repository-side.")

    logger.info(f"Агент обновлён: {agent_id}")
    return updated_agent

@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(
    agent_id: str,
    agent_repo: AgentRepository = Depends(get_agent_repository)
):
    agent = await agent_repo.get_by_id(agent_id)
    if not agent:
        logger.warning(f"Агент не найден для удаления: {agent_id}")
        raise HTTPException(status_code=404, detail="Agent not found")
    await agent_repo.delete(agent_id)
    logger.info(f"Агент удалён: {agent_id}")
    return None 