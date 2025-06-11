#!/usr/bin/env python3
"""
🏭 Производственное развертывание - KittyCore 2.0 (1 час)

Полный пример продакшн-готового агента с мониторингом,
логированием, обработкой ошибок и масштабированием.
"""

import os
import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path

from kittycore import Agent
from kittycore.tools import WebSearchTool, EmailTool
from kittycore.memory import PersistentMemory
from kittycore.config import Config

# Настройка продакшн логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('production_agent.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class ProductionConfig:
    """Конфигурация для продакшн развертывания"""
    agent_name: str = "ProductionAssistant"
    max_concurrent_requests: int = 10
    request_timeout: int = 30
    memory_file: str = "production_memory.json"
    metrics_file: str = "agent_metrics.json"
    log_level: str = "INFO"
    backup_interval: int = 3600  # секунд
    health_check_interval: int = 60  # секунд

class ProductionAgent:
    """Продакшн-готовый агент с полным мониторингом"""
    
    def __init__(self, config: ProductionConfig):
        self.config = config
        self.metrics = {
            "requests_total": 0,
            "requests_successful": 0,
            "requests_failed": 0,
            "uptime_start": datetime.now().isoformat(),
            "last_request": None,
            "error_log": []
        }
        
        # Создать продакшн агента
        self.agent = Agent(
            prompt="""
            Ты продакшн AI помощник для бизнеса.
            
            Твои задачи:
            - Отвечать на запросы клиентов профессионально
            - Использовать инструменты для получения актуальной информации
            - Логировать все важные действия
            - Обрабатывать ошибки gracefully
            - Поддерживать высокую скорость ответов
            
            Принципы:
            - Безопасность превыше всего
            - Всегда проверяй информацию
            - Будь вежлив и профессионален
            - Логируй критические операции
            """,
            tools=[
                WebSearchTool(max_results=5),
                EmailTool()
            ],
            memory=PersistentMemory(file_path=config.memory_file),
            name=config.agent_name
        )
        
        self.semaphore = asyncio.Semaphore(config.max_concurrent_requests)
        self._running = False
        self._tasks = set()
        
        logger.info(f"Продакшн агент {config.agent_name} инициализирован")
    
    async def process_request(self, request_id: str, user_input: str, 
                            metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """Обработать запрос с полным логированием и мониторингом"""
        async with self.semaphore:
            start_time = datetime.now()
            
            try:
                logger.info(f"Обработка запроса {request_id}: {user_input[:100]}...")
                
                # Обновить метрики
                self.metrics["requests_total"] += 1
                self.metrics["last_request"] = start_time.isoformat()
                
                # Добавить контекст к запросу
                enhanced_input = f"""
                Запрос ID: {request_id}
                Время: {start_time.isoformat()}
                Метаданные: {json.dumps(metadata or {}, ensure_ascii=False)}
                
                Пользовательский запрос: {user_input}
                """
                
                # Выполнить запрос с таймаутом
                response = await asyncio.wait_for(
                    asyncio.create_task(self._run_agent(enhanced_input)),
                    timeout=self.config.request_timeout
                )
                
                # Успешная обработка
                processing_time = (datetime.now() - start_time).total_seconds()
                self.metrics["requests_successful"] += 1
                
                result = {
                    "success": True,
                    "request_id": request_id,
                    "response": response,
                    "processing_time": processing_time,
                    "timestamp": start_time.isoformat()
                }
                
                logger.info(f"Запрос {request_id} обработан за {processing_time:.2f}с")
                return result
                
            except asyncio.TimeoutError:
                self._handle_error(request_id, "Timeout", "Превышено время ожидания")
                return {
                    "success": False,
                    "request_id": request_id,
                    "error": "timeout",
                    "message": "Превышено время ожидания обработки"
                }
                
            except Exception as e:
                self._handle_error(request_id, type(e).__name__, str(e))
                return {
                    "success": False,
                    "request_id": request_id,
                    "error": "processing_error",
                    "message": f"Ошибка обработки: {str(e)}"
                }
    
    async def _run_agent(self, input_text: str) -> str:
        """Запустить агента в отдельной задаче"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.agent.run, input_text)
    
    def _handle_error(self, request_id: str, error_type: str, error_message: str):
        """Обработать ошибку с логированием"""
        self.metrics["requests_failed"] += 1
        
        error_entry = {
            "request_id": request_id,
            "error_type": error_type,
            "error_message": error_message,
            "timestamp": datetime.now().isoformat()
        }
        
        self.metrics["error_log"].append(error_entry)
        
        # Ограничить размер лога ошибок
        if len(self.metrics["error_log"]) > 100:
            self.metrics["error_log"] = self.metrics["error_log"][-50:]
        
        logger.error(f"Ошибка в запросе {request_id}: {error_type} - {error_message}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Проверка здоровья системы"""
        try:
            # Тест простого запроса
            test_start = datetime.now()
            test_response = await asyncio.wait_for(
                self._run_agent("Тестовый запрос для проверки здоровья"),
                timeout=5.0
            )
            response_time = (datetime.now() - test_start).total_seconds()
            
            # Статистика памяти
            memory_stats = self.agent.memory.get_stats() if hasattr(self.agent.memory, 'get_stats') else {}
            
            return {
                "status": "healthy",
                "response_time": response_time,
                "uptime": self._get_uptime(),
                "metrics": self.metrics.copy(),
                "memory_stats": memory_stats,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _get_uptime(self) -> float:
        """Получить время работы в секундах"""
        start_time = datetime.fromisoformat(self.metrics["uptime_start"])
        return (datetime.now() - start_time).total_seconds()
    
    def save_metrics(self):
        """Сохранить метрики в файл"""
        try:
            with open(self.config.metrics_file, 'w', encoding='utf-8') as f:
                json.dump(self.metrics, f, ensure_ascii=False, indent=2)
            logger.info(f"Метрики сохранены в {self.config.metrics_file}")
        except Exception as e:
            logger.error(f"Ошибка сохранения метрик: {e}")
    
    async def start_monitoring(self):
        """Запустить фоновый мониторинг"""
        self._running = True
        
        async def monitor_loop():
            while self._running:
                try:
                    # Автосохранение метрик
                    self.save_metrics()
                    
                    # Health check
                    health = await self.health_check()
                    if health["status"] != "healthy":
                        logger.warning(f"Health check warning: {health}")
                    
                    await asyncio.sleep(self.config.health_check_interval)
                    
                except Exception as e:
                    logger.error(f"Ошибка мониторинга: {e}")
                    await asyncio.sleep(10)
        
        task = asyncio.create_task(monitor_loop())
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)
        
        logger.info("Мониторинг запущен")
    
    async def stop(self):
        """Graceful shutdown"""
        logger.info("Останавливаем продакшн агента...")
        self._running = False
        
        # Дождаться завершения задач
        if self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)
        
        # Финальное сохранение метрик
        self.save_metrics()
        logger.info("Продакшн агент остановлен")

async def main():
    """Основная функция для демонстрации продакшн системы"""
    print("🏭 Запуск продакшн агента...")
    
    # Создать конфигурацию
    config = ProductionConfig(
        agent_name="CustomerSupportPro",
        max_concurrent_requests=5,
        request_timeout=15
    )
    
    # Создать продакшн агента
    prod_agent = ProductionAgent(config)
    
    # Запустить мониторинг
    await prod_agent.start_monitoring()
    
    print("✅ Продакшн агент запущен")
    print("📊 Доступные команды:")
    print("  'health' - проверка здоровья")
    print("  'metrics' - показать метрики")
    print("  'load <N>' - нагрузочный тест с N запросами")
    print("  'выход' - остановить систему")
    print("-" * 50)
    
    try:
        while True:
            user_input = input("\n👤 Команда или запрос: ")
            
            if user_input.lower() in ['выход', 'quit', 'exit']:
                break
            elif user_input.lower() == 'health':
                health = await prod_agent.health_check()
                print(f"🏥 Здоровье системы: {json.dumps(health, ensure_ascii=False, indent=2)}")
            elif user_input.lower() == 'metrics':
                print(f"📊 Метрики: {json.dumps(prod_agent.metrics, ensure_ascii=False, indent=2)}")
            elif user_input.startswith('load '):
                try:
                    count = int(user_input.split()[1])
                    print(f"🔥 Запуск нагрузочного теста с {count} запросами...")
                    
                    tasks = []
                    for i in range(count):
                        task = prod_agent.process_request(
                            f"load_test_{i}",
                            f"Тестовый запрос №{i}",
                            {"test": True, "batch": "load_test"}
                        )
                        tasks.append(task)
                    
                    results = await asyncio.gather(*tasks)
                    successful = sum(1 for r in results if r["success"])
                    print(f"✅ Завершено: {successful}/{count} успешных запросов")
                    
                except ValueError:
                    print("❌ Неверный формат команды. Используйте: load <число>")
            else:
                # Обычный запрос
                request_id = f"req_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                result = await prod_agent.process_request(request_id, user_input)
                
                if result["success"]:
                    print(f"🤖 Ответ: {result['response']}")
                    print(f"⏱️ Время обработки: {result['processing_time']:.2f}с")
                else:
                    print(f"❌ Ошибка: {result['message']}")
    
    except KeyboardInterrupt:
        print("\n🛑 Получен сигнал остановки...")
    
    finally:
        await prod_agent.stop()
        print("👋 Продакшн агент остановлен")

if __name__ == "__main__":
    print("🐱 KittyCore 2.0 - Продакшн развертывание")
    print("=" * 50)
    
    # Настройка среды
    if not os.getenv('OPENROUTER_API_KEY'):
        print("⚠️  Установите OPENROUTER_API_KEY для полной функциональности")
        os.environ['OPENROUTER_API_KEY'] = 'demo-key'
    
    asyncio.run(main()) 