#!/usr/bin/env python3
"""
🧪 РЕАЛЬНЫЙ ТЕСТЕР ONTOBOT СЦЕНАРИЕВ
Выполняет реальные сценарии с настоящими плагинами, показывая каждый шаг
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, Any
import aiohttp
from loguru import logger

# Настройка логирования
logger.add("logs/real_ontobot_tester.log", 
          format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | REAL_TEST | {message}",
          level="INFO", rotation="10 MB", compression="zip")

class RealOntoBotTester:
    """Тестер реальных сценариев OntoBot с пошаговым выполнением."""
    
    def __init__(self, kittycore_url: str = "http://localhost:8085"):
        self.kittycore_url = kittycore_url
        self.test_results = []
        self.step_counter = 0
        
        logger.info("🧪 Real OntoBot Tester инициализирован")
        
    async def test_mongo_operations(self, user_id: int = 99997) -> Dict[str, Any]:
        """Тест операций с MongoDB через плагины."""
        
        logger.info(f"🗄️ НАЧИНАЕМ ТЕСТ: MongoDB операции для пользователя {user_id}")
        
        test_start = time.time()
        operations_results = []
        
        try:
            # 1. Тест вставки документа
            logger.info("📝 ШАГ 1: Вставка тестового пользователя в MongoDB")
            
            insert_result = await self._call_kittycore_api("/api/v1/simple/mongo/insert", {
                "collection": "test_users",
                "document": {
                    "user_id": user_id,
                    "name": "Тестовый Пользователь",
                    "stage": "testing",
                    "created_at": datetime.now().isoformat(),
                    "test_data": {
                        "ya_ya_response": "Я недостаточно хорош",
                        "ya_delo_response": "Я боюсь начать свой проект",
                        "ya_relations_response": "Меня все равно бросят"
                    }
                }
            })
            
            operations_results.append({
                "operation": "insert",
                "success": insert_result.get("success", False),
                "data": insert_result.get("data", {})
            })
            
            logger.info(f"✅ Вставка: {insert_result.get('success', False)}")
            
            # 2. Тест поиска документа
            logger.info("🔍 ШАГ 2: Поиск пользователя в MongoDB")
            
            find_result = await self._call_kittycore_api("/api/v1/simple/mongo/find", {
                "collection": "test_users",
                "filter": {"user_id": user_id}
            })
            
            operations_results.append({
                "operation": "find",
                "success": find_result.get("success", False),
                "data": find_result.get("data", [])
            })
            
            logger.info(f"✅ Поиск: {find_result.get('success', False)}, найдено: {len(find_result.get('data', []))}")
            
            # 3. Тест обновления документа
            logger.info("📝 ШАГ 3: Обновление пользователя в MongoDB")
            
            update_result = await self._call_kittycore_api("/api/v1/simple/mongo/update", {
                "collection": "test_users",
                "filter": {"user_id": user_id},
                "document": {
                    "$set": {
                        "stage": "diagnostic_completed",
                        "updated_at": datetime.now().isoformat(),
                        "test_data.diagnostic_score": 85
                    }
                }
            })
            
            operations_results.append({
                "operation": "update",
                "success": update_result.get("success", False),
                "data": update_result.get("data", {})
            })
            
            logger.info(f"✅ Обновление: {update_result.get('success', False)}")
            
            # 4. Тест удаления документа
            logger.info("🗑️ ШАГ 4: Удаление тестового пользователя")
            
            delete_result = await self._call_kittycore_api("/api/v1/simple/mongo/delete", {
                "collection": "test_users",
                "filter": {"user_id": user_id}
            })
            
            operations_results.append({
                "operation": "delete",
                "success": delete_result.get("success", False),
                "data": delete_result.get("data", {})
            })
            
            logger.info(f"✅ Удаление: {delete_result.get('success', False)}")
            
            duration = time.time() - test_start
            all_success = all(op["success"] for op in operations_results)
            
            test_result = {
                "test_name": "mongo_operations",
                "success": all_success,
                "duration": duration,
                "operations": operations_results,
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"✅ MONGO ТЕСТ ЗАВЕРШЕН: {all_success}, операций: {len(operations_results)}")
            
            return test_result
            
        except Exception as e:
            logger.error(f"❌ ОШИБКА В MONGO ТЕСТЕ: {str(e)}")
            return {
                "test_name": "mongo_operations",
                "success": False,
                "error": str(e),
                "duration": time.time() - test_start,
                "timestamp": datetime.now().isoformat()
            }
    
    async def test_llm_integration(self) -> Dict[str, Any]:
        """Тест интеграции с LLM плагином."""
        
        logger.info("🤖 НАЧИНАЕМ ТЕСТ: LLM интеграция")
        
        test_start = time.time()
        
        try:
            # Тест LLM запроса для генерации досье
            logger.info("💭 ШАГ 1: Генерация досье через LLM")
            
            llm_context = {
                "ya_ya_response": "Я недостаточно хорош, всегда все порчу, меня сложно любить",
                "ya_delo_response": "Я боюсь начать свой проект, у меня недостаточно опыта",
                "ya_relations_response": "Меня все равно бросят, никто меня не понимает"
            }
            
            # Выполняем шаг LLM через движок
            llm_step = {
                "id": "test_llm_dossier",
                "type": "llm_chat",
                "params": {
                    "messages": [
                        {
                            "role": "system",
                            "content": "Ты ИИ-ассистент проекта Onto Nothing, создающий персонализированные досье мыслевирусов."
                        },
                        {
                            "role": "user", 
                            "content": f"""Создай краткое досье для пользователя на основе его ответов:

Сфера "Я-Я": {llm_context['ya_ya_response']}
Сфера "Я-Дело": {llm_context['ya_delo_response']}
Сфера "Я-Отношения": {llm_context['ya_relations_response']}

Структура досье:
1. ГЛАВНЫЕ МЫСЛЕВИРУСЫ (2-3 ключевых)
2. КРАТКИЙ ПРОГНОЗ (что будет если не изменится)
3. РЕКОМЕНДАЦИИ (первые шаги)

Объем: до 300 слов."""
                        }
                    ],
                    "model": "gpt-4",
                    "temperature": 0.7,
                    "output_var": "generated_dossier"
                }
            }
            
            llm_result = await self._call_kittycore_api("/api/v1/simple/execute", {
                "step": llm_step,
                "context": llm_context
            })
            
            duration = time.time() - test_start
            
            test_result = {
                "test_name": "llm_integration",
                "success": llm_result.get("success", False),
                "duration": duration,
                "generated_dossier": llm_result.get("context", {}).get("generated_dossier", ""),
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"✅ LLM ТЕСТ ЗАВЕРШЕН: {test_result['success']}")
            if test_result["generated_dossier"]:
                logger.info(f"📄 Сгенерированное досье: {test_result['generated_dossier'][:200]}...")
            
            return test_result
            
        except Exception as e:
            logger.error(f"❌ ОШИБКА В LLM ТЕСТЕ: {str(e)}")
            return {
                "test_name": "llm_integration",
                "success": False,
                "error": str(e),
                "duration": time.time() - test_start,
                "timestamp": datetime.now().isoformat()
            }
    
    async def test_scenario_execution(self, user_id: int = 99999) -> Dict[str, Any]:
        """Тест выполнения реального сценария mr_ontobot_main_router."""
        
        logger.info(f"🎬 НАЧИНАЕМ ТЕСТ: Выполнение сценария mr_ontobot_main_router для пользователя {user_id}")
        
        test_start = time.time()
        
        try:
            # Подготовка контекста
            initial_context = {
                "user_id": str(user_id),
                "chat_id": str(user_id),
                "telegram_first_name": "Тестовый",
                "telegram_last_name": "Пользователь", 
                "telegram_username": "test_user",
                "phone_number": "+79991234567",
                "current_timestamp": datetime.now().isoformat(),
                "test_mode": True
            }
            
            logger.info(f"📋 Начальный контекст: {json.dumps(initial_context, ensure_ascii=False, indent=2)}")
            
            # Выполняем сценарий через KittyCore API
            result = await self._call_kittycore_api(f"/api/v1/simple/channels/test/execute", {
                "scenario_id": "mr_ontobot_main_router",
                "context": initial_context
            })
            
            duration = time.time() - test_start
            
            test_result = {
                "test_name": "scenario_execution",
                "success": result.get("success", False),
                "duration": duration,
                "final_context": result.get("final_context", {}),
                "scenario_id": result.get("scenario_id"),
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"✅ СЦЕНАРИЙ ЗАВЕРШЕН: {test_result['success']}, время: {duration:.2f}с")
            
            return test_result
            
        except Exception as e:
            logger.error(f"❌ ОШИБКА В СЦЕНАРИИ: {str(e)}")
            return {
                "test_name": "scenario_execution",
                "success": False,
                "error": str(e),
                "duration": time.time() - test_start,
                "timestamp": datetime.now().isoformat()
            }
    
    async def _call_kittycore_api(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Вызывает API KittyCore."""
        
        url = f"{self.kittycore_url}{endpoint}"
        
        logger.info(f"🌐 API ВЫЗОВ: {endpoint}")
        logger.info(f"📤 ДАННЫЕ: {json.dumps(data, ensure_ascii=False, indent=2)}")
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data) as response:
                result = await response.json()
                
                logger.info(f"📥 ОТВЕТ: {json.dumps(result, ensure_ascii=False, indent=2)}")
                
                return result

    async def run_all_tests(self) -> Dict[str, Any]:
        """Запускает все тесты последовательно."""
        
        logger.info("🚀 ЗАПУСК ВСЕХ ТЕСТОВ ONTOBOT")
        
        all_start = time.time()
        all_results = []
        
        # 1. Тест MongoDB операций
        logger.info("\n" + "="*60)
        logger.info("🗄️ ТЕСТ 1: MongoDB операции")
        logger.info("="*60)
        
        mongo_result = await self.test_mongo_operations()
        all_results.append(mongo_result)
        
        # 2. Тест LLM интеграции
        logger.info("\n" + "="*60)
        logger.info("🤖 ТЕСТ 2: LLM интеграция")
        logger.info("="*60)
        
        llm_result = await self.test_llm_integration()
        all_results.append(llm_result)
        
        # 3. Тест выполнения сценария
        logger.info("\n" + "="*60)
        logger.info("🎬 ТЕСТ 3: Выполнение сценария")
        logger.info("="*60)
        
        scenario_result = await self.test_scenario_execution()
        all_results.append(scenario_result)
        
        total_duration = time.time() - all_start
        successful_tests = sum(1 for r in all_results if r.get("success", False))
        
        summary = {
            "total_tests": len(all_results),
            "successful_tests": successful_tests,
            "failed_tests": len(all_results) - successful_tests,
            "total_duration": total_duration,
            "success_rate": (successful_tests / len(all_results)) * 100,
            "results": all_results,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info("\n" + "="*60)
        logger.info("📊 ИТОГОВЫЕ РЕЗУЛЬТАТЫ")
        logger.info("="*60)
        logger.info(f"✅ Успешных тестов: {successful_tests}/{len(all_results)}")
        logger.info(f"📈 Процент успеха: {summary['success_rate']:.1f}%")
        logger.info(f"⏱️ Общее время: {total_duration:.2f} секунд")
        
        return summary

async def main():
    """Главная функция для запуска тестов."""
    
    print("🧪 РЕАЛЬНЫЙ ТЕСТЕР ONTOBOT СЦЕНАРИЕВ")
    print("="*50)
    
    tester = RealOntoBotTester()
    
    # Проверяем доступность KittyCore
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{tester.kittycore_url}/health") as response:
                if response.status == 200:
                    print("✅ KittyCore API доступен")
                else:
                    print("❌ KittyCore API недоступен")
                    return
    except Exception as e:
        print(f"❌ Ошибка подключения к KittyCore: {e}")
        return
    
    # Запускаем все тесты
    results = await tester.run_all_tests()
    
    print(f"\n📊 ИТОГОВЫЕ РЕЗУЛЬТАТЫ:")
    print(f"✅ Успешных тестов: {results['successful_tests']}/{results['total_tests']}")
    print(f"📈 Процент успеха: {results['success_rate']:.1f}%")
    print(f"⏱️ Общее время: {results['total_duration']:.2f} секунд")
    
    # Сохраняем результаты
    with open("logs/real_ontobot_test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 Результаты сохранены в logs/real_ontobot_test_results.json")
    print(f"📋 Логи доступны в logs/real_ontobot_tester.log")

if __name__ == "__main__":
    asyncio.run(main())
