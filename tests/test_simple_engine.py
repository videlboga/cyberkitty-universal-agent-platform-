"""
Unit тесты для SimpleScenarioEngine.
Проверяем базовую функциональность нового упрощенного движка.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from app.core.simple_engine import SimpleScenarioEngine, StopExecution
from app.core.base_plugin import BasePlugin


class MockPlugin(BasePlugin):
    """Тестовый плагин для unit тестов."""
    
    def __init__(self):
        super().__init__("mock_plugin")
        self.healthcheck_result = True
        self.handler_called = False
        
    def register_handlers(self):
        return {
            "mock_step": self.handle_mock_step,
            "telegram_send_message": self.handle_telegram_send
        }
        
    async def healthcheck(self):
        return self.healthcheck_result
        
    async def handle_mock_step(self, step, context):
        self.handler_called = True
        context["mock_executed"] = True
        return context
        
    async def handle_telegram_send(self, step, context):
        context["message_sent"] = step.get("params", {}).get("text", "test message")
        return context


class TestSimpleScenarioEngine:
    """Тесты для SimpleScenarioEngine."""
    
    def setup_method(self):
        """Создаем новый движок для каждого теста."""
        self.engine = SimpleScenarioEngine()
        
    def test_engine_initialization(self):
        """Тест инициализации движка."""
        assert self.engine.step_handlers is not None
        assert self.engine.plugins == {}
        
        # Проверяем что базовые обработчики зарегистрированы
        expected_handlers = ["start", "end", "action", "input"]
        for handler in expected_handlers:
            assert handler in self.engine.step_handlers
            
    def test_register_plugin(self):
        """Тест регистрации плагина."""
        plugin = MockPlugin()
        
        # Регистрируем плагин
        self.engine.register_plugin(plugin)
        
        # Проверяем что плагин зарегистрирован
        assert "mock_plugin" in self.engine.plugins
        assert self.engine.plugins["mock_plugin"] == plugin
        
        # Проверяем что обработчики плагина добавлены
        assert "mock_step" in self.engine.step_handlers
        assert "telegram_send_message" in self.engine.step_handlers
        
    @pytest.mark.asyncio
    async def test_healthcheck(self):
        """Тест healthcheck движка и плагинов."""
        plugin = MockPlugin()
        self.engine.register_plugin(plugin)
        
        # Тест успешного healthcheck
        health = await self.engine.healthcheck()
        assert health["engine"] is True
        assert health["mock_plugin"] is True
        
        # Тест неудачного healthcheck плагина
        plugin.healthcheck_result = False
        health = await self.engine.healthcheck()
        assert health["engine"] is True
        assert health["mock_plugin"] is False
        
    @pytest.mark.asyncio
    async def test_execute_step_basic(self):
        """Тест выполнения базовых шагов."""
        context = {"user_id": "test123"}
        
        # Тест шага start
        step = {"id": "step1", "type": "start"}
        result = await self.engine.execute_step(step, context)
        assert result["user_id"] == "test123"
        
        # Тест шага end
        step = {"id": "step2", "type": "end"}
        result = await self.engine.execute_step(step, context)
        assert result["execution_completed"] is True
        
    @pytest.mark.asyncio
    async def test_execute_step_plugin(self):
        """Тест выполнения шагов через плагин."""
        plugin = MockPlugin()
        self.engine.register_plugin(plugin)
        
        context = {"user_id": "test123"}
        step = {"id": "step1", "type": "mock_step"}
        
        result = await self.engine.execute_step(step, context)
        
        # Проверяем что плагин был вызван
        assert plugin.handler_called is True
        assert result["mock_executed"] is True
        assert result["user_id"] == "test123"
        
    @pytest.mark.asyncio
    async def test_execute_step_unknown_type(self):
        """Тест обработки неизвестного типа шага."""
        context = {"user_id": "test123"}
        step = {"id": "step1", "type": "unknown_step_type"}
        
        with pytest.raises(ValueError, match="Неизвестный тип шага"):
            await self.engine.execute_step(step, context)
            
    @pytest.mark.asyncio
    async def test_execute_step_input(self):
        """Тест шага input - должен остановить выполнение."""
        context = {"user_id": "test123"}
        step = {"id": "input1", "type": "input"}
        
        with pytest.raises(StopExecution):
            await self.engine.execute_step(step, context)
            
    def test_find_first_step(self):
        """Тест поиска первого шага."""
        steps = [
            {"id": "step1", "type": "action"},
            {"id": "start_step", "type": "start"},
            {"id": "step2", "type": "end"}
        ]
        
        first_step = self.engine._find_first_step(steps)
        assert first_step["id"] == "start_step"
        assert first_step["type"] == "start"
        
        # Тест когда нет start шага
        steps_no_start = [
            {"id": "step1", "type": "action"},
            {"id": "step2", "type": "end"}
        ]
        
        first_step = self.engine._find_first_step(steps_no_start)
        assert first_step["id"] == "step1"
        
    def test_find_next_step(self):
        """Тест поиска следующего шага."""
        steps = [
            {"id": "step1", "type": "start", "next_step": "step2"},
            {"id": "step2", "type": "action", "next_step": "step3"},
            {"id": "step3", "type": "end"}
        ]
        
        current_step = {"id": "step1", "next_step": "step2"}
        context = {}
        
        next_step = self.engine._find_next_step(steps, current_step, context)
        assert next_step["id"] == "step2"
        
        # Тест когда следующего шага нет
        current_step = {"id": "step3"}  # Нет next_step
        next_step = self.engine._find_next_step(steps, current_step, context)
        assert next_step is None
        
    @pytest.mark.asyncio
    async def test_execute_scenario_simple(self):
        """Тест выполнения простого сценария."""
        plugin = MockPlugin()
        self.engine.register_plugin(plugin)
        
        scenario = {
            "scenario_id": "test_scenario",
            "steps": [
                {"id": "start", "type": "start", "next_step": "action1"},
                {"id": "action1", "type": "mock_step", "next_step": "end"},
                {"id": "end", "type": "end"}
            ]
        }
        
        context = {"user_id": "test123"}
        
        result = await self.engine.execute_scenario(scenario, context)
        
        # Проверяем результат
        assert result["user_id"] == "test123"
        assert result["scenario_id"] == "test_scenario"
        assert result["execution_started"] is True
        assert result["execution_completed"] is True
        assert result["mock_executed"] is True
        assert plugin.handler_called is True
        
    @pytest.mark.asyncio
    async def test_execute_scenario_with_input_stop(self):
        """Тест выполнения сценария с остановкой на input."""
        scenario = {
            "scenario_id": "test_input_scenario", 
            "steps": [
                {"id": "start", "type": "start", "next_step": "input1"},
                {"id": "input1", "type": "input", "next_step": "end"},
                {"id": "end", "type": "end"}
            ]
        }
        
        context = {"user_id": "test123"}
        
        with pytest.raises(StopExecution):
            await self.engine.execute_scenario(scenario, context)
            
    def test_get_registered_handlers(self):
        """Тест получения списка обработчиков."""
        plugin = MockPlugin()
        self.engine.register_plugin(plugin)
        
        handlers = self.engine.get_registered_handlers()
        
        # Базовые обработчики
        assert "start" in handlers
        assert "end" in handlers
        assert "action" in handlers
        assert "input" in handlers
        
        # Обработчики плагина
        assert "mock_step" in handlers
        assert "telegram_send_message" in handlers
        
    def test_get_registered_plugins(self):
        """Тест получения списка плагинов."""
        plugin1 = MockPlugin()
        plugin1.name = "plugin1"
        
        plugin2 = MockPlugin() 
        plugin2.name = "plugin2"
        
        self.engine.register_plugin(plugin1)
        self.engine.register_plugin(plugin2)
        
        plugins = self.engine.get_registered_plugins()
        assert "plugin1" in plugins
        assert "plugin2" in plugins
        assert len(plugins) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 