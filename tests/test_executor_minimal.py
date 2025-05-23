import pytest
from app.models.scenario import Scenario
from app.core.scenario_executor import ScenarioExecutor
import json
import os

@pytest.mark.asyncio
async def test_minimal_no_plugins():
    # Загружаем сценарий
    scenario_path = os.path.join(os.path.dirname(__file__), '../docs/examples/test_minimal_no_plugins.json')
    with open(scenario_path, 'r', encoding='utf-8') as f:
        scenario_data = json.load(f)
    scenario = Scenario(**scenario_data)

    # Инициализируем executor без плагинов
    executor = ScenarioExecutor(plugins=[])

    # Выполняем сценарий
    result_context = await executor.execute_scenario(scenario, context=scenario.initial_context)

    # Проверяем, что ошибок нет
    assert '__step_error__' not in result_context
    # Проверяем, что сценарий дошёл до конца
    assert 'test_flag' in result_context
    # Проверяем, что логика ветвления сработала (test_flag=True => ветка TRUE)
    # (Ветка определяется по логам, но можно проверить, что не было ошибок и context не изменился) 