#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестирование настроек плагинов напрямую.
Проверяет работу с настройками БЕЗ зависимости от API.
"""

import pytest
import asyncio
from datetime import datetime
from typing import Dict, Any

# Импортируем только актуальные плагины
from app.plugins.mongo_plugin import MongoPlugin
from app.plugins.simple_llm_plugin import SimpleLLMPlugin
from app.plugins.simple_amocrm_plugin import SimpleAmoCRMPlugin


class TestActualPluginSettings:
    """Тестирование настроек актуальных плагинов"""
    
    @pytest.fixture
    async def mongo_plugin(self):
        """Создает MongoDB плагин для тестов"""
        plugin = MongoPlugin()
        await plugin.initialize()
        return plugin
    
    @pytest.fixture  
    async def llm_plugin(self):
        """Создает LLM плагин для тестов"""
        plugin = SimpleLLMPlugin()
        await plugin.initialize()
        return plugin
        
    @pytest.fixture
    async def amocrm_plugin(self):
        """Создает AmoCRM плагин для тестов"""
        plugin = SimpleAmoCRMPlugin()
        await plugin.initialize()
        return plugin

    async def test_mongo_plugin_settings(self, mongo_plugin):
        """Тестирует настройки MongoDB плагина"""
        # MongoDB плагин обычно не требует настроек
        healthcheck = await mongo_plugin.healthcheck()
        assert isinstance(healthcheck, bool)
        
    async def test_llm_plugin_settings(self, llm_plugin):
        """Тестирует настройки LLM плагина"""
        # Проверяем что плагин инициализирован
        assert llm_plugin.name == "simple_llm"
        
        # Проверяем healthcheck
        healthcheck = await llm_plugin.healthcheck()
        assert isinstance(healthcheck, bool)
        
    async def test_amocrm_plugin_settings(self, amocrm_plugin):
        """Тестирует настройки AmoCRM плагина"""
        # Проверяем что плагин инициализирован
        assert amocrm_plugin.name == "simple_amocrm"
        
        # Проверяем healthcheck (должен быть False без настроек)
        healthcheck = await amocrm_plugin.healthcheck()
        assert isinstance(healthcheck, bool)
        
    async def test_plugin_handlers_registration(self, mongo_plugin, llm_plugin, amocrm_plugin):
        """Тестирует регистрацию обработчиков плагинов"""
        
        # MongoDB handlers
        mongo_handlers = mongo_plugin.register_handlers()
        assert isinstance(mongo_handlers, dict)
        assert len(mongo_handlers) > 0
        assert "mongo_find_documents" in mongo_handlers
        
        # LLM handlers
        llm_handlers = llm_plugin.register_handlers()
        assert isinstance(llm_handlers, dict)
        assert len(llm_handlers) > 0
        assert "llm_query" in llm_handlers
        
        # AmoCRM handlers
        amocrm_handlers = amocrm_plugin.register_handlers()
        assert isinstance(amocrm_handlers, dict)
        assert len(amocrm_handlers) > 0
        assert "amocrm_find_contact" in amocrm_handlers


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 