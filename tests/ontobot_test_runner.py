#!/usr/bin/env python3
"""
🧪 ONTOBOT TEST RUNNER
Простой запуск автотестов для OntoBot сценариев

Возможности:
- Запуск тестов с мокированным Telegram API
- Проверка прохождения сценариев
- Генерация отчетов
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
import aiohttp
from loguru import logger

# Настройка логирования
logger.add(
    "logs/ontobot_tests.log",
    rotation="10 MB",
    retention="7 days",
    compression="gz",
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | TEST | {message}",
    level="INFO"
)

class OntoTestRunner:
    """
    Простой запуск тестов OntoBot сценариев.
    
    Интегрируется с:
    - Telegram Mock Server
    - User Simulator
    - KittyCore API
    """
    
    def __init__(self, 
                 kittycore_url: str = "http://localhost:8085",
                 mock_server_url: str = "http://localhost:8082"):
        self.kittycore_url = kittycore_url
        self.mock_server_url = mock_server_url
        self.test_results: List[Dict[str, Any]] = []
        
        logger.info("🧪 OntoBot Test Runner инициализирован")
    
    async def test_mr_ontobot_welcome(self, user_id: int = 12345) -> Dict[str, Any]:
        """Тест приветственного сценария Mr OntoBot."""
        
        test_name = "mr_ontobot_welcome"
        logger.info(f"🚀 Запуск теста: {test_name}")
        
        start_time = time.time()
        
        try:
            # 1. Очищаем мок сервер
            await self._clear_mock_server()
            
            # 2. Запускаем сценарий через KittyCore API
            response = await self._execute_scenario(
                scenario_id="mr_ontobot_main_router",
                user_id=user_id,
                context={
                    "test_mode": True,
                    "telegram_api_url": self.mock_server_url
                }
            )
            
            # 3. Проверяем результат
            success = response.get("success", False)
            
            # 4. Получаем сообщения из мок сервера
            messages = await self._get_mock_messages(user_id)
            
            # 5. Проверяем что приветственное сообщение отправлено
            welcome_found = False
            for msg in messages.get("messages", []):
                if "Привет! Я – ИИ-ассистент" in msg.get("text", ""):
                    welcome_found = True
                    break
            
            duration = time.time() - start_time
            
            result = {
                "test_name": test_name,
                "success": success and welcome_found,
                "duration": duration,
                "messages_count": len(messages.get("messages", [])),
                "welcome_message_found": welcome_found,
                "response": response,
                "timestamp": datetime.now().isoformat()
            }
            
            self.test_results.append(result)
            
            if result["success"]:
                logger.info(f"✅ Тест {test_name} прошел успешно за {duration:.2f}с")
            else:
                logger.error(f"❌ Тест {test_name} провален")
            
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            
            result = {
                "test_name": test_name,
                "success": False,
                "duration": duration,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            
            self.test_results.append(result)
            logger.error(f"❌ Ошибка в тесте {test_name}: {e}")
            
            return result
    
    async def test_user_interaction(self, user_id: int = 12346) -> Dict[str, Any]:
        """Тест взаимодействия пользователя с ботом."""
        
        test_name = "user_interaction"
        logger.info(f"🚀 Запуск теста: {test_name}")
        
        start_time = time.time()
        
        try:
            # Импортируем User Simulator
            from .user_simulator import UserSimulator
            
            simulator = UserSimulator(self.mock_server_url)
            
            # 1. Очищаем мок сервер
            await self._clear_mock_server()
            
            # 2. Создаем тестового пользователя
            user = simulator.create_user(user_id, "активный")
            
            # 3. Пользователь отправляет /start
            await simulator.send_message(user_id, "/start")
            
            # 4. Ждем ответа бота
            await asyncio.sleep(2)
            
            # 5. Получаем сообщения
            messages = await self._get_mock_messages(user_id)
            
            # 6. Проверяем что бот ответил
            bot_messages = [
                msg for msg in messages.get("messages", [])
                if msg.get("from", {}).get("is_bot", False)
            ]
            
            duration = time.time() - start_time
            
            result = {
                "test_name": test_name,
                "success": len(bot_messages) > 0,
                "duration": duration,
                "user_messages": len(messages.get("messages", [])) - len(bot_messages),
                "bot_messages": len(bot_messages),
                "timestamp": datetime.now().isoformat()
            }
            
            self.test_results.append(result)
            
            if result["success"]:
                logger.info(f"✅ Тест {test_name} прошел успешно за {duration:.2f}с")
            else:
                logger.error(f"❌ Тест {test_name} провален")
            
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            
            result = {
                "test_name": test_name,
                "success": False,
                "duration": duration,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            
            self.test_results.append(result)
            logger.error(f"❌ Ошибка в тесте {test_name}: {e}")
            
            return result
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Запускает все тесты OntoBot."""
        
        logger.info("🚀 Запуск всех тестов OntoBot")
        
        start_time = time.time()
        
        # Список всех тестов
        tests = [
            self.test_mr_ontobot_welcome,
            self.test_user_interaction
        ]
        
        # Запускаем тесты последовательно
        for test_func in tests:
            try:
                await test_func()
                # Пауза между тестами
                await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"❌ Критическая ошибка в тесте: {e}")
        
        duration = time.time() - start_time
        
        # Подсчитываем результаты
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["success"]])
        failed_tests = total_tests - passed_tests
        
        summary = {
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            "total_duration": duration,
            "timestamp": datetime.now().isoformat(),
            "results": self.test_results
        }
        
        logger.info(f"📊 Тесты завершены: {passed_tests}/{total_tests} прошли за {duration:.2f}с")
        
        return summary
    
    async def _execute_scenario(self, scenario_id: str, user_id: int, context: Dict[str, Any]) -> Dict[str, Any]:
        """Выполняет сценарий через KittyCore API."""
        
        payload = {
            "user_id": str(user_id),
            "chat_id": str(user_id),
            "scenario_id": scenario_id,
            "context": context
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.kittycore_url}/api/v1/simple/channels/test_channel/execute",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    return await response.json()
                    
        except Exception as e:
            logger.error(f"❌ Ошибка выполнения сценария: {e}")
            return {"success": False, "error": str(e)}
    
    async def _clear_mock_server(self):
        """Очищает данные мок сервера."""
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.delete(
                    f"{self.mock_server_url}/mock/clear"
                ) as response:
                    result = await response.json()
                    logger.debug("🧹 Мок сервер очищен")
                    return result
                    
        except Exception as e:
            logger.warning(f"⚠️ Не удалось очистить мок сервер: {e}")
    
    async def _get_mock_messages(self, chat_id: int = None) -> Dict[str, Any]:
        """Получает сообщения из мок сервера."""
        
        try:
            url = f"{self.mock_server_url}/mock/messages"
            if chat_id:
                url += f"?chat_id={chat_id}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    return await response.json()
                    
        except Exception as e:
            logger.error(f"❌ Ошибка получения сообщений: {e}")
            return {"messages": [], "count": 0}
    
    def save_report(self, filename: str = None):
        """Сохраняет отчет о тестах в файл."""
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"logs/ontobot_test_report_{timestamp}.json"
        
        summary = {
            "test_run": {
                "timestamp": datetime.now().isoformat(),
                "total_tests": len(self.test_results),
                "passed": len([r for r in self.test_results if r["success"]]),
                "failed": len([r for r in self.test_results if not r["success"]])
            },
            "results": self.test_results
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(summary, f, ensure_ascii=False, indent=2)
            
            logger.info(f"📄 Отчет сохранен: {filename}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения отчета: {e}")

# === ПРОСТОЙ ЗАПУСК ===

async def main():
    """Простой запуск тестов."""
    
    logger.info("🚀 Запуск автотестов OntoBot")
    
    # Создаем тест раннер
    runner = OntoTestRunner()
    
    # Запускаем все тесты
    summary = await runner.run_all_tests()
    
    # Сохраняем отчет
    runner.save_report()
    
    # Выводим результаты
    print("\n" + "="*50)
    print("📊 РЕЗУЛЬТАТЫ ТЕСТОВ ONTOBOT")
    print("="*50)
    print(f"Всего тестов: {summary['total_tests']}")
    print(f"Прошли: {summary['passed']}")
    print(f"Провалились: {summary['failed']}")
    print(f"Успешность: {summary['success_rate']:.1f}%")
    print(f"Время выполнения: {summary['total_duration']:.2f}с")
    print("="*50)
    
    if summary['failed'] > 0:
        print("\n❌ ПРОВАЛИВШИЕСЯ ТЕСТЫ:")
        for result in summary['results']:
            if not result['success']:
                print(f"  - {result['test_name']}: {result.get('error', 'Неизвестная ошибка')}")
    
    logger.info("✅ Автотесты завершены")

if __name__ == "__main__":
    asyncio.run(main()) 