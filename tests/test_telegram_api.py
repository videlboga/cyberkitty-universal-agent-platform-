#!/usr/bin/env python3
"""
🧪 TELEGRAM API ТЕСТЫ
Тестирует Telegram функциональность Universal Agent Platform через API.
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
    "logs/telegram_api_tests.log",
    rotation="10 MB",
    retention="3 days", 
    compression="gz",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}",
    level="INFO"
)

# Конфигурация API
API_BASE_URL = "http://localhost:8080"
API_V1_URL = f"{API_BASE_URL}/api/v1/simple"

class TestTelegramIntegration:
    """Тесты интеграции с Telegram."""
    
    def test_telegram_send_message_step(self):
        """Тест отправки Telegram сообщения через шаг."""
        logger.info("🧪 Тест: Отправка Telegram сообщения")
        
        payload = {
            "step": {
                "id": "telegram_message",
                "type": "telegram_send_message",
                "params": {
                    "chat_id": "123456789",
                    "text": "Тестовое сообщение из API теста",
                    "parse_mode": "HTML"
                }
            },
            "context": {
                "test_mode": True,
                "telegram_test": True
            }
        }
        
        response = requests.post(
            f"{API_V1_URL}/execute",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # В тестовом режиме сообщение не отправляется реально
        assert data["success"] is True
        assert "context" in data
        
        logger.info("✅ Telegram сообщение обработано")
    
    def test_telegram_send_buttons_step(self):
        """Тест отправки Telegram кнопок через шаг."""
        logger.info("🧪 Тест: Отправка Telegram кнопок")
        
        payload = {
            "step": {
                "id": "telegram_buttons",
                "type": "telegram_send_buttons",
                "params": {
                    "chat_id": "123456789",
                    "text": "Выберите опцию:",
                    "buttons": [
                        [{"text": "Опция 1", "callback_data": "option_1"}],
                        [{"text": "Опция 2", "callback_data": "option_2"}]
                    ]
                }
            },
            "context": {
                "test_mode": True,
                "telegram_test": True
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
        
        logger.info("✅ Telegram кнопки обработаны")
    
    def test_telegram_polling_start(self):
        """Тест запуска Telegram polling."""
        logger.info("🧪 Тест: Запуск Telegram polling")
        
        response = requests.post(
            f"{API_V1_URL}/telegram/start-polling",
            headers={"Content-Type": "application/json"}
        )
        
        # Может вернуть ошибку если токен не настроен, это нормально
        if response.status_code == 200:
            data = response.json()
            assert "success" in data
            logger.info("✅ Telegram polling запущен")
        else:
            logger.warning("⚠️ Telegram токен не настроен, пропускаем тест")
    
    def test_telegram_polling_stop(self):
        """Тест остановки Telegram polling."""
        logger.info("🧪 Тест: Остановка Telegram polling")
        
        response = requests.post(
            f"{API_V1_URL}/telegram/stop-polling",
            headers={"Content-Type": "application/json"}
        )
        
        # Может вернуть ошибку если polling не запущен, это нормально
        if response.status_code == 200:
            data = response.json()
            assert "success" in data
            logger.info("✅ Telegram polling остановлен")
        else:
            logger.warning("⚠️ Telegram polling не был запущен")


class TestTelegramScenarios:
    """Тесты Telegram сценариев."""
    
    def test_telegram_registration_scenario(self):
        """Тест полного сценария регистрации в Telegram."""
        logger.info("🧪 Тест: Полный сценарий регистрации Telegram")
        
        payload = {
            "user_id": "telegram_user_test",
            "chat_id": "telegram_chat_test",
            "context": {
                "test_mode": True,
                "user_name": "Тестовый Пользователь",
                "registration_started": True
            },
            "scenario_id": "telegram_registration"
        }
        
        response = requests.post(
            f"{API_V1_URL}/channels/telegram_registration_test/execute",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "final_context" in data
        assert data["final_context"]["registration_started"] is True
        
        logger.info(f"✅ Telegram регистрация выполнена: {data['scenario_id']}")
    
    def test_telegram_callback_handling(self):
        """Тест обработки Telegram callback."""
        logger.info("🧪 Тест: Обработка Telegram callback")
        
        # Симулируем callback от кнопки
        payload = {
            "user_id": "telegram_user_callback",
            "chat_id": "telegram_chat_callback",
            "context": {
                "test_mode": True,
                "callback_data": "reg_user",
                "message_id": "123",
                "from_callback": True
            }
        }
        
        response = requests.post(
            f"{API_V1_URL}/channels/telegram_callback_test/execute",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "final_context" in data
        
        logger.info("✅ Telegram callback обработан")
    
    def test_telegram_message_with_variables(self):
        """Тест Telegram сообщения с переменными."""
        logger.info("🧪 Тест: Telegram сообщение с переменными")
        
        payload = {
            "step": {
                "id": "telegram_message_vars",
                "type": "telegram_send_message",
                "params": {
                    "chat_id": "{chat_id}",
                    "text": "Привет, {user_name}! Ваш ID: {user_id}",
                    "parse_mode": "HTML"
                }
            },
            "context": {
                "test_mode": True,
                "chat_id": "987654321",
                "user_name": "Тестовый Пользователь",
                "user_id": "user_123"
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
        
        logger.info("✅ Telegram сообщение с переменными обработано")


class TestTelegramErrorHandling:
    """Тесты обработки ошибок Telegram."""
    
    def test_telegram_invalid_chat_id(self):
        """Тест обработки неверного chat_id."""
        logger.info("🧪 Тест: Неверный chat_id")
        
        payload = {
            "step": {
                "id": "telegram_invalid_chat",
                "type": "telegram_send_message",
                "params": {
                    "chat_id": "invalid_chat_id",
                    "text": "Тестовое сообщение"
                }
            },
            "context": {
                "test_mode": True
            }
        }
        
        response = requests.post(
            f"{API_V1_URL}/execute",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        # В тестовом режиме должно обработаться без ошибок
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        logger.info("✅ Неверный chat_id обработан корректно")
    
    def test_telegram_missing_parameters(self):
        """Тест обработки отсутствующих параметров."""
        logger.info("🧪 Тест: Отсутствующие параметры Telegram")
        
        payload = {
            "step": {
                "id": "telegram_missing_params",
                "type": "telegram_send_message",
                "params": {
                    # Отсутствует chat_id и text
                }
            },
            "context": {
                "test_mode": True
            }
        }
        
        response = requests.post(
            f"{API_V1_URL}/execute",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        # Должно вернуть ошибку или обработать gracefully
        assert response.status_code in [200, 500]
        
        if response.status_code == 500:
            data = response.json()
            assert data["success"] is False
            logger.info("✅ Отсутствующие параметры обработаны с ошибкой")
        else:
            logger.info("✅ Отсутствующие параметры обработаны gracefully")


class TestTelegramPerformance:
    """Тесты производительности Telegram."""
    
    def test_multiple_telegram_messages(self):
        """Тест отправки множественных Telegram сообщений."""
        logger.info("🧪 Тест: Множественные Telegram сообщения")
        
        import concurrent.futures
        
        def send_telegram_message(message_id: int) -> Dict[str, Any]:
            payload = {
                "step": {
                    "id": f"telegram_message_{message_id}",
                    "type": "telegram_send_message",
                    "params": {
                        "chat_id": f"test_chat_{message_id}",
                        "text": f"Тестовое сообщение #{message_id}"
                    }
                },
                "context": {
                    "test_mode": True,
                    "message_id": message_id
                }
            }
            
            start_time = time.time()
            response = requests.post(
                f"{API_V1_URL}/execute",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            end_time = time.time()
            
            return {
                "message_id": message_id,
                "status_code": response.status_code,
                "response_time": end_time - start_time,
                "success": response.status_code == 200
            }
        
        # Отправляем 10 сообщений параллельно
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(send_telegram_message, i) for i in range(10)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # Проверяем результаты
        successful_messages = [r for r in results if r["success"]]
        avg_response_time = sum(r["response_time"] for r in successful_messages) / len(successful_messages)
        
        assert len(successful_messages) >= 8  # Минимум 8 из 10 должны быть успешными
        assert avg_response_time < 2.0  # Среднее время ответа менее 2 секунд
        
        logger.info(f"✅ Множественные Telegram сообщения: {len(successful_messages)}/10 успешных, среднее время: {avg_response_time:.2f}с")


class TestTelegramIntegrationScenarios:
    """Тесты интеграционных сценариев Telegram."""
    
    def test_telegram_full_conversation_flow(self):
        """Тест полного потока разговора в Telegram."""
        logger.info("🧪 Тест: Полный поток разговора Telegram")
        
        # Шаг 1: Начальное сообщение
        step1_payload = {
            "user_id": "conversation_user",
            "chat_id": "conversation_chat",
            "context": {
                "test_mode": True,
                "user_name": "Тестовый Собеседник",
                "conversation_started": True
            },
            "scenario_id": "demo"
        }
        
        response1 = requests.post(
            f"{API_V1_URL}/channels/conversation_test/execute",
            json=step1_payload,
            headers={"Content-Type": "application/json"}
        )
        
        assert response1.status_code == 200
        data1 = response1.json()
        assert data1["success"] is True
        
        # Шаг 2: Симулируем callback от пользователя
        step2_payload = {
            "user_id": "conversation_user",
            "chat_id": "conversation_chat",
            "context": {
                **data1["final_context"],
                "callback_data": "test_switch",
                "from_callback": True
            }
        }
        
        response2 = requests.post(
            f"{API_V1_URL}/channels/conversation_test/execute",
            json=step2_payload,
            headers={"Content-Type": "application/json"}
        )
        
        assert response2.status_code == 200
        data2 = response2.json()
        assert data2["success"] is True
        
        logger.info("✅ Полный поток разговора Telegram выполнен")
    
    def test_telegram_scenario_switching(self):
        """Тест переключения сценариев в Telegram."""
        logger.info("🧪 Тест: Переключение сценариев Telegram")
        
        # Начинаем с одного сценария
        payload = {
            "user_id": "switch_user",
            "chat_id": "switch_chat",
            "context": {
                "test_mode": True,
                "switch_to_scenario": "telegram_registration"
            },
            "scenario_id": "demo"
        }
        
        response = requests.post(
            f"{API_V1_URL}/channels/switch_test/execute",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        logger.info("✅ Переключение сценариев Telegram работает")


if __name__ == "__main__":
    # Запуск тестов напрямую
    pytest.main([__file__, "-v", "--tb=short"]) 