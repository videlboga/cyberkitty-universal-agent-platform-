import asyncio
import json
from typing import Dict, Any, Callable, List, Optional
from loguru import logger

from app.plugins.plugin_base import PluginBase


class OrchestratorPlugin(PluginBase):
    def __init__(self):
        super().__init__()
        
    def register_step_handlers(self, step_handlers: Dict[str, Callable]):
        """Регистрирует обработчики шагов, предоставляемые этим плагином."""
        step_handlers["execute_scenario"] = self.handle_execute_scenario
        step_handlers["execute_scenarios_parallel"] = self.handle_execute_scenarios_parallel
        step_handlers["execute_scenarios_sequence"] = self.handle_execute_scenarios_sequence
        step_handlers["conditional_execute"] = self.handle_conditional_execute
        logger.info(f"OrchestratorPlugin зарегистрировал обработчики шагов: execute_scenario, execute_scenarios_parallel, execute_scenarios_sequence, conditional_execute")

    async def handle_execute_scenario(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Выполняет один под-сценарий."""
        params = step_data.get("params", {})
        
        scenario_id = params.get("scenario_id")
        agent_id = params.get("agent_id")
        input_context = params.get("input_context", {})
        output_mapping = params.get("output_mapping", {})
        timeout_seconds = params.get("timeout_seconds", 300)  # 5 минут по умолчанию
        
        if not scenario_id:
            logger.error("execute_scenario: scenario_id is required")
            return None
            
        logger.info(f"Executing sub-scenario: {scenario_id} with agent: {agent_id}")
        
        # Подготавливаем контекст для под-сценария
        sub_context = self._prepare_input_context(input_context, context)
        
        try:
            # Выполняем под-сценарий
            result = await asyncio.wait_for(
                self._execute_sub_scenario(scenario_id, agent_id, sub_context),
                timeout=timeout_seconds
            )
            
            # Обрабатываем результат
            self._process_output_mapping(result, output_mapping, context, params.get("output_var"))
            
            logger.info(f"Sub-scenario {scenario_id} completed successfully")
            
        except asyncio.TimeoutError:
            logger.error(f"Sub-scenario {scenario_id} timed out after {timeout_seconds} seconds")
            output_var = params.get("output_var", "sub_scenario_result")
            context[output_var] = {"status": "timeout", "error": "Scenario execution timed out"}
            
        except Exception as e:
            logger.error(f"Sub-scenario {scenario_id} failed: {str(e)}")
            output_var = params.get("output_var", "sub_scenario_result")
            context[output_var] = {"status": "error", "error": str(e)}
            
        return None

    async def handle_execute_scenarios_parallel(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Выполняет несколько сценариев параллельно."""
        params = step_data.get("params", {})
        
        scenarios = params.get("scenarios", [])
        timeout_seconds = params.get("timeout_seconds", 600)  # 10 минут по умолчанию
        wait_for_all = params.get("wait_for_all", True)
        
        if not scenarios:
            logger.error("execute_scenarios_parallel: scenarios list is required")
            return None
            
        logger.info(f"Executing {len(scenarios)} scenarios in parallel")
        
        # Создаём задачи для каждого сценария
        tasks = []
        for i, scenario_config in enumerate(scenarios):
            scenario_id = scenario_config.get("scenario_id")
            agent_id = scenario_config.get("agent_id")
            input_context = scenario_config.get("input_context", {})
            
            if not scenario_id:
                logger.warning(f"Scenario {i} missing scenario_id, skipping")
                continue
                
            sub_context = self._prepare_input_context(input_context, context)
            task = asyncio.create_task(
                self._execute_sub_scenario(scenario_id, agent_id, sub_context),
                name=f"scenario_{scenario_id}_{i}"
            )
            tasks.append((task, scenario_config))
            
        if not tasks:
            logger.error("No valid scenarios to execute")
            return None
            
        try:
            if wait_for_all:
                # Ждём завершения всех сценариев
                results = await asyncio.wait_for(
                    asyncio.gather(*[task for task, _ in tasks], return_exceptions=True),
                    timeout=timeout_seconds
                )
            else:
                # Ждём завершения первого успешного сценария
                done, pending = await asyncio.wait_for(
                    asyncio.wait([task for task, _ in tasks], return_when=asyncio.FIRST_COMPLETED),
                    timeout=timeout_seconds
                )
                # Отменяем остальные задачи
                for task in pending:
                    task.cancel()
                results = [task.result() for task in done]
                
            # Обрабатываем результаты
            parallel_results = []
            for i, (result, scenario_config) in enumerate(zip(results, [config for _, config in tasks])):
                if isinstance(result, Exception):
                    parallel_results.append({
                        "scenario_id": scenario_config.get("scenario_id"),
                        "status": "error",
                        "error": str(result)
                    })
                else:
                    parallel_results.append({
                        "scenario_id": scenario_config.get("scenario_id"),
                        "status": "success",
                        "result": result
                    })
                    
            output_var = params.get("output_var", "parallel_results")
            context[output_var] = parallel_results
            
            logger.info(f"Parallel execution completed: {len(parallel_results)} results")
            
        except asyncio.TimeoutError:
            logger.error(f"Parallel execution timed out after {timeout_seconds} seconds")
            output_var = params.get("output_var", "parallel_results")
            context[output_var] = {"status": "timeout", "error": "Parallel execution timed out"}
            
        return None

    async def handle_execute_scenarios_sequence(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Выполняет сценарии последовательно."""
        params = step_data.get("params", {})
        
        scenarios = params.get("scenarios", [])
        stop_on_error = params.get("stop_on_error", True)
        pass_context = params.get("pass_context", True)  # Передавать контекст между сценариями
        
        if not scenarios:
            logger.error("execute_scenarios_sequence: scenarios list is required")
            return None
            
        logger.info(f"Executing {len(scenarios)} scenarios in sequence")
        
        sequence_results = []
        current_context = dict(context)  # Копия контекста
        
        for i, scenario_config in enumerate(scenarios):
            scenario_id = scenario_config.get("scenario_id")
            agent_id = scenario_config.get("agent_id")
            input_context = scenario_config.get("input_context", {})
            
            if not scenario_id:
                logger.warning(f"Scenario {i} missing scenario_id, skipping")
                continue
                
            logger.info(f"Executing sequence step {i+1}/{len(scenarios)}: {scenario_id}")
            
            try:
                # Подготавливаем контекст
                if pass_context:
                    sub_context = self._prepare_input_context(input_context, current_context)
                else:
                    sub_context = self._prepare_input_context(input_context, context)
                    
                # Выполняем сценарий
                result = await self._execute_sub_scenario(scenario_id, agent_id, sub_context)
                
                sequence_results.append({
                    "scenario_id": scenario_id,
                    "status": "success",
                    "result": result
                })
                
                # Обновляем контекст для следующего сценария
                if pass_context and isinstance(result, dict):
                    current_context.update(result)
                    
                logger.info(f"Sequence step {i+1} completed successfully")
                
            except Exception as e:
                logger.error(f"Sequence step {i+1} failed: {str(e)}")
                
                sequence_results.append({
                    "scenario_id": scenario_id,
                    "status": "error",
                    "error": str(e)
                })
                
                if stop_on_error:
                    logger.info("Stopping sequence execution due to error")
                    break
                    
        output_var = params.get("output_var", "sequence_results")
        context[output_var] = sequence_results
        
        # Обновляем основной контекст
        if pass_context:
            context.update(current_context)
            
        logger.info(f"Sequence execution completed: {len(sequence_results)} steps")
        return None

    async def handle_conditional_execute(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Выполняет сценарии условно на основе правил."""
        params = step_data.get("params", {})
        
        conditions = params.get("conditions", [])
        default_scenario = params.get("default_scenario")
        
        if not conditions:
            logger.error("conditional_execute: conditions list is required")
            return None
            
        logger.info(f"Evaluating {len(conditions)} conditions for scenario execution")
        
        executed_scenario = None
        
        # Проверяем условия по порядку
        for condition_config in conditions:
            condition = condition_config.get("condition")
            scenario_id = condition_config.get("scenario_id")
            agent_id = condition_config.get("agent_id")
            input_context = condition_config.get("input_context", {})
            
            if not condition or not scenario_id:
                logger.warning("Condition missing condition or scenario_id, skipping")
                continue
                
            try:
                # Вычисляем условие
                if eval(condition, {"context": context}):
                    logger.info(f"Condition '{condition}' is true, executing scenario: {scenario_id}")
                    
                    sub_context = self._prepare_input_context(input_context, context)
                    result = await self._execute_sub_scenario(scenario_id, agent_id, sub_context)
                    
                    executed_scenario = {
                        "scenario_id": scenario_id,
                        "condition": condition,
                        "status": "success",
                        "result": result
                    }
                    break
                    
            except Exception as e:
                logger.error(f"Error evaluating condition '{condition}': {str(e)}")
                executed_scenario = {
                    "scenario_id": scenario_id,
                    "condition": condition,
                    "status": "error",
                    "error": str(e)
                }
                break
                
        # Если ни одно условие не сработало, выполняем default сценарий
        if not executed_scenario and default_scenario:
            logger.info(f"No conditions matched, executing default scenario: {default_scenario.get('scenario_id')}")
            
            scenario_id = default_scenario.get("scenario_id")
            agent_id = default_scenario.get("agent_id")
            input_context = default_scenario.get("input_context", {})
            
            try:
                sub_context = self._prepare_input_context(input_context, context)
                result = await self._execute_sub_scenario(scenario_id, agent_id, sub_context)
                
                executed_scenario = {
                    "scenario_id": scenario_id,
                    "condition": "default",
                    "status": "success",
                    "result": result
                }
            except Exception as e:
                executed_scenario = {
                    "scenario_id": scenario_id,
                    "condition": "default",
                    "status": "error",
                    "error": str(e)
                }
                
        output_var = params.get("output_var", "conditional_result")
        context[output_var] = executed_scenario or {"status": "no_match"}
        
        return None

    def _prepare_input_context(self, input_context: Dict[str, Any], source_context: Dict[str, Any]) -> Dict[str, Any]:
        """Подготавливает контекст для под-сценария."""
        # Начинаем с копии исходного контекста
        prepared_context = dict(source_context)
        
        # Добавляем/перезаписываем значения из input_context
        for key, value in input_context.items():
            if isinstance(value, str) and "{" in value and "}" in value:
                # Разрешаем переменные в значениях
                try:
                    prepared_context[key] = value.format(**source_context)
                except KeyError as e:
                    logger.warning(f"Variable {e} not found in context for key {key}")
                    prepared_context[key] = value
            else:
                prepared_context[key] = value
                
        return prepared_context

    def _process_output_mapping(self, result: Dict[str, Any], output_mapping: Dict[str, Any], 
                               context: Dict[str, Any], output_var: Optional[str]):
        """Обрабатывает маппинг результатов в контекст."""
        if output_var:
            context[output_var] = result
            
        if output_mapping and isinstance(result, dict):
            for target_key, source_key in output_mapping.items():
                if source_key in result:
                    context[target_key] = result[source_key]
                else:
                    logger.warning(f"Output mapping key '{source_key}' not found in result")

    async def _execute_sub_scenario(self, scenario_id: str, agent_id: Optional[str], 
                                   sub_context: Dict[str, Any]) -> Dict[str, Any]:
        """Выполняет под-сценарий."""
        logger.info(f"Executing sub-scenario: {scenario_id}")
        
        # Заглушка для выполнения сценария
        # В реальной реализации здесь должна быть интеграция с ScenarioExecutor
        # Пример: return await self.scenario_executor.execute_scenario(scenario_id, agent_id, sub_context)
        
        # Имитация выполнения
        await asyncio.sleep(0.1)
        
        return {
            "scenario_id": scenario_id,
            "agent_id": agent_id,
            "status": "completed",
            "final_context": sub_context
        }

    async def healthcheck(self) -> Dict[str, Any]:
        """Проверка состояния оркестратора."""
        return {
            "status": "healthy",
            "available_handlers": ["execute_scenario", "execute_scenarios_parallel", 
                                 "execute_scenarios_sequence", "conditional_execute"]
        } 