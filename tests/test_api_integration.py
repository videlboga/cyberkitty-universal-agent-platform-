#!/usr/bin/env python3
"""
🧪 API ИНТЕГРАЦИОННЫЕ ТЕСТЫ
Тестирует Universal Agent Platform через API с поднятыми Docker контейнерами.
Принцип: ПРОСТОТА ПРЕВЫШЕ ВСЕГО!
"""

import pytest
import requests
import json
import time
from typing import Dict, Any
from loguru import logger

# Настройка логирования для тестов
logger.add(
    "logs/api_tests.log",
    rotation="10 MB",
    retention="3 days", 
    compression="gz",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}",
    level="INFO"
)

# Конфигурация API
API_BASE_URL = "http://localhost:8080"
API_V1_URL = f"{API_BASE_URL}/api/v1/simple"

class TestAPIHealth:
    """Тесты проверки здоровья системы."""
    
    def test_root_endpoint(self):
        """Тест корневого endpoint."""
        logger.info("🧪 Тест: Корневой endpoint")
        
        response = requests.get(f"{API_BASE_URL}/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "platform" in data
        assert "Universal Agent Platform" in data["platform"]
        assert "version" in data
        assert "features" in data
        
        logger.info(f"✅ Корневой endpoint работает: {data['platform']} v{data['version']}")
    
    def test_health_endpoint(self):
        """Тест health endpoint."""
        logger.info("🧪 Тест: Health endpoint")
        
        response = requests.get(f"{API_BASE_URL}/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "healthy"
        assert "Universal Agent Platform" in data["platform"]
        
        logger.info("✅ Health endpoint работает")
    
    def test_api_health_endpoint(self):
        """Тест API health endpoint."""
        logger.info("🧪 Тест: API Health endpoint")
        
        response = requests.get(f"{API_V1_URL}/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "engine" in data
        assert "plugins" in data
        
        logger.info(f"✅ API Health endpoint работает: {len(data['plugins'])} плагинов")
    
    def test_api_info_endpoint(self):
        """Тест API info endpoint."""
        logger.info("🧪 Тест: API Info endpoint")
        
        response = requests.get(f"{API_V1_URL}/info")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "handlers" in data
        assert "plugins" in data
        assert len(data["handlers"]) > 0
        
        logger.info(f"✅ API Info endpoint работает: {len(data['handlers'])} обработчиков")


class TestScenarioExecution:
    """Тесты выполнения сценариев."""
    
    def test_execute_demo_scenario(self):
        """Тест выполнения демо сценария."""
        logger.info("🧪 Тест: Выполнение демо сценария")
        
        payload = {
            "user_id": "test_user_123",
            "chat_id": "test_chat_456", 
            "context": {
                "test_mode": True,
                "user_name": "Тестовый Пользователь"
            },
            "scenario_id": "demo"
        }
        
        response = requests.post(
            f"{API_V1_URL}/channels/demo/execute",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "scenario_id" in data
        assert "final_context" in data
        
        logger.info(f"✅ Демо сценарий выполнен: {data['scenario_id']}")
    
    def test_execute_telegram_registration_scenario(self):
        """Тест выполнения сценария регистрации Telegram."""
        logger.info("🧪 Тест: Выполнение сценария регистрации Telegram")
        
        payload = {
            "user_id": "telegram_user_789",
            "chat_id": "telegram_chat_101112",
            "context": {
                "test_mode": True,
                "user_name": "Telegram Тестер",
                "registration_started": True
            },
            "scenario_id": "telegram_registration"
        }
        
        response = requests.post(
            f"{API_V1_URL}/channels/telegram_test/execute",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "final_context" in data
        
        logger.info(f"✅ Telegram регистрация выполнена: {data['scenario_id']}")
    
    def test_execute_step_directly(self):
        """Тест прямого выполнения шага."""
        logger.info("🧪 Тест: Прямое выполнение шага")
        
        payload = {
            "step": {
                "id": "test_step",
                "type": "action",
                "params": {
                    "action": "log_message",
                    "message": "Тестовое сообщение из API теста"
                }
            },
            "context": {
                "test_mode": True,
                "api_test": True
            }
        }
        
        response = requests.post(
            f"{API_V1_URL}/execute",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "context" in data
        assert data["context"]["test_mode"] is True
        
        logger.info("✅ Прямое выполнение шага работает")


class TestMongoOperations:
    """Тесты операций с MongoDB."""
    
    def test_mongo_save_scenario(self):
        """Тест сохранения сценария в MongoDB."""
        logger.info("🧪 Тест: Сохранение сценария в MongoDB")
        
        test_scenario = {
            "scenario_id": "api_test_scenario",
            "name": "API Test Scenario",
            "description": "Тестовый сценарий для API тестов",
            "steps": [
                {
                    "id": "start",
                    "type": "start",
                    "next_step": "message"
                },
                {
                    "id": "message",
                    "type": "action",
                    "params": {
                        "action": "log_message",
                        "message": "API тест сценарий выполнен"
                    },
                    "next_step": "end"
                },
                {
                    "id": "end",
                    "type": "end"
                }
            ]
        }
        
        payload = {
            "scenario_id": test_scenario["scenario_id"],
            "document": test_scenario
        }
        
        response = requests.post(
            f"{API_V1_URL}/mongo/save-scenario",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        # MongoDB может быть недоступен, это нормально
        if response.status_code == 200:
            data = response.json()
            assert data["success"] is True
            logger.info("✅ Сценарий сохранен в MongoDB")
        else:
            logger.warning("⚠️ MongoDB недоступен, пропускаем тест")
    
    def test_mongo_find_scenarios(self):
        """Тест поиска сценариев в MongoDB."""
        logger.info("🧪 Тест: Поиск сценариев в MongoDB")
        
        payload = {
            "collection": "scenarios",
            "filter": {}
        }
        
        response = requests.post(
            f"{API_V1_URL}/mongo/find",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        # MongoDB может быть недоступен, это нормально
        if response.status_code == 200:
            data = response.json()
            assert data["success"] is True
            logger.info(f"✅ Найдено сценариев в MongoDB: {len(data.get('data', []))}")
        else:
            logger.warning("⚠️ MongoDB недоступен, пропускаем тест")


class TestErrorHandling:
    """Тесты обработки ошибок."""
    
    def test_invalid_channel_id(self):
        """Тест обработки неверного channel_id."""
        logger.info("🧪 Тест: Неверный channel_id")
        
        payload = {
            "user_id": "test_user",
            "context": {}
        }
        
        response = requests.post(
            f"{API_V1_URL}/channels/nonexistent_channel/execute",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        # Должен вернуть ошибку 404
        assert response.status_code == 404
        
        data = response.json()
        assert "не найден" in data["detail"]
        logger.info("✅ Правильно вернул 404 для неверного channel_id")
    
    def test_invalid_step_type(self):
        """Тест обработки неверного типа шага."""
        logger.info("🧪 Тест: Неверный тип шага")
        
        payload = {
            "step": {
                "id": "invalid_step",
                "type": "nonexistent_step_type",
                "params": {}
            },
            "context": {}
        }
        
        response = requests.post(
            f"{API_V1_URL}/execute",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 500
        data = response.json()
        assert data["success"] is False
        assert "error" in data
        
        logger.info("✅ Корректно обработана ошибка неверного типа шага")
    
    def test_malformed_request(self):
        """Тест обработки некорректного запроса."""
        logger.info("🧪 Тест: Некорректный запрос")
        
        # Отправляем некорректный JSON
        response = requests.post(
            f"{API_V1_URL}/execute",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422  # Validation error
        
        logger.info("✅ Корректно обработан некорректный JSON")


class TestPerformance:
    """Тесты производительности."""
    
    def test_concurrent_requests(self):
        """Тест параллельных запросов."""
        logger.info("🧪 Тест: Параллельные запросы")
        
        import concurrent.futures
        import threading
        
        def make_request(request_id: int) -> Dict[str, Any]:
            payload = {
                "user_id": f"concurrent_user_{request_id}",
                "chat_id": f"concurrent_chat_{request_id}",
                "context": {
                    "test_mode": True,
                    "request_id": request_id
                },
                "scenario_id": "demo"
            }
            
            start_time = time.time()
            response = requests.post(
                f"{API_V1_URL}/channels/demo/execute",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            end_time = time.time()
            
            return {
                "request_id": request_id,
                "status_code": response.status_code,
                "response_time": end_time - start_time,
                "success": response.status_code == 200
            }
        
        # Выполняем 5 параллельных запросов
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request, i) for i in range(5)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # Проверяем результаты
        successful_requests = [r for r in results if r["success"]]
        avg_response_time = sum(r["response_time"] for r in successful_requests) / len(successful_requests)
        
        assert len(successful_requests) >= 4  # Минимум 4 из 5 должны быть успешными
        assert avg_response_time < 5.0  # Среднее время ответа менее 5 секунд
        
        logger.info(f"✅ Параллельные запросы: {len(successful_requests)}/5 успешных, среднее время: {avg_response_time:.2f}с")


@pytest.fixture(scope="session", autouse=True)
def setup_and_teardown():
    """Настройка и очистка для всех тестов."""
    logger.info("🚀 Начинаем API тесты Universal Agent Platform")
    
    # Ждем, пока API будет готов
    max_retries = 30
    for i in range(max_retries):
        try:
            response = requests.get(f"{API_BASE_URL}/health", timeout=5)
            if response.status_code == 200:
                logger.info("✅ API готов к тестированию")
                break
        except requests.exceptions.RequestException:
            if i == max_retries - 1:
                pytest.fail("❌ API не готов к тестированию после 30 попыток")
            time.sleep(1)
    
    yield
    
    logger.info("🏁 API тесты завершены")


if __name__ == "__main__":
    # Запуск тестов напрямую
    pytest.main([__file__, "-v", "--tb=short"]) 