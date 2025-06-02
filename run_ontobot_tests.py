#!/usr/bin/env python3
"""
🚀 ЗАПУСК АВТОТЕСТОВ ONTOBOT
Простой скрипт для запуска всей системы тестирования

Запускает:
1. Telegram Mock Server (порт 8081)
2. OntoBot Test Runner
3. Генерирует отчеты
"""

import asyncio
import subprocess
import time
import signal
import sys
from pathlib import Path
from loguru import logger

# Настройка логирования
logger.add(
    "logs/test_launcher.log",
    rotation="10 MB",
    retention="7 days",
    compression="gz",
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | LAUNCHER | {message}",
    level="INFO"
)

class OntoTestLauncher:
    """Запускает всю систему автотестов OntoBot."""
    
    def __init__(self):
        self.mock_server_process = None
        self.running = True
        
        # Обработчик сигналов для корректного завершения
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        logger.info("🚀 OntoBot Test Launcher инициализирован")
    
    def _signal_handler(self, signum, frame):
        """Обработчик сигналов для корректного завершения."""
        logger.info(f"📡 Получен сигнал {signum}, завершаем работу...")
        self.running = False
        self._cleanup()
        sys.exit(0)
    
    def _cleanup(self):
        """Очистка ресурсов."""
        if self.mock_server_process:
            logger.info("🛑 Останавливаем Mock Server...")
            self.mock_server_process.terminate()
            try:
                self.mock_server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                logger.warning("⚠️ Mock Server не остановился, принудительно завершаем")
                self.mock_server_process.kill()
    
    async def start_mock_server(self):
        """Запускает Telegram Mock Server."""
        logger.info("🤖 Запуск Telegram Mock Server...")
        
        try:
            # Запускаем мок сервер в отдельном процессе
            self.mock_server_process = subprocess.Popen([
                sys.executable, "tests/telegram_mock_server.py"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Ждем запуска сервера
            await asyncio.sleep(3)
            
            # Проверяем что процесс запустился
            if self.mock_server_process.poll() is None:
                logger.info("✅ Telegram Mock Server запущен на порту 8082")
                return True
            else:
                logger.error("❌ Не удалось запустить Mock Server")
                return False
                
        except Exception as e:
            logger.error(f"❌ Ошибка запуска Mock Server: {e}")
            return False
    
    async def check_kittycore_api(self):
        """Проверяет доступность KittyCore API."""
        logger.info("🔍 Проверка KittyCore API...")
        
        try:
            import aiohttp
            
            async with aiohttp.ClientSession() as session:
                async with session.get("http://localhost:8085/health") as response:
                    if response.status == 200:
                        logger.info("✅ KittyCore API доступен")
                        return True
                    else:
                        logger.warning(f"⚠️ KittyCore API вернул статус {response.status}")
                        return False
                        
        except Exception as e:
            logger.warning(f"⚠️ KittyCore API недоступен: {e}")
            logger.info("💡 Убедитесь что KittyCore запущен на порту 8085")
            return False
    
    async def run_tests(self):
        """Запускает тесты OntoBot."""
        logger.info("🧪 Запуск тестов OntoBot...")
        
        try:
            from tests.ontobot_test_runner import OntoTestRunner
            
            # Создаем тест раннер
            runner = OntoTestRunner()
            
            # Запускаем все тесты
            summary = await runner.run_all_tests()
            
            # Сохраняем отчет
            runner.save_report()
            
            return summary
            
        except Exception as e:
            logger.error(f"❌ Ошибка запуска тестов: {e}")
            return None
    
    async def run_full_test_cycle(self):
        """Запускает полный цикл тестирования."""
        logger.info("🚀 Запуск полного цикла тестирования OntoBot")
        
        try:
            # 1. Запускаем Mock Server
            if not await self.start_mock_server():
                logger.error("❌ Не удалось запустить Mock Server, прерываем тесты")
                return
            
            # 2. Проверяем KittyCore API (опционально)
            await self.check_kittycore_api()
            
            # 3. Запускаем тесты
            summary = await self.run_tests()
            
            if summary:
                # 4. Выводим результаты
                self._print_summary(summary)
                
                # 5. Возвращаем код выхода
                if summary['failed'] > 0:
                    logger.warning("⚠️ Некоторые тесты провалились")
                    return 1
                else:
                    logger.info("✅ Все тесты прошли успешно")
                    return 0
            else:
                logger.error("❌ Не удалось запустить тесты")
                return 1
                
        except Exception as e:
            logger.error(f"❌ Критическая ошибка: {e}")
            return 1
        
        finally:
            # Очистка ресурсов
            self._cleanup()
    
    def _print_summary(self, summary):
        """Выводит красивый отчет о тестах."""
        
        print("\n" + "="*60)
        print("🧪 ОТЧЕТ О ТЕСТИРОВАНИИ ONTOBOT")
        print("="*60)
        print(f"📊 Всего тестов: {summary['total_tests']}")
        print(f"✅ Прошли: {summary['passed']}")
        print(f"❌ Провалились: {summary['failed']}")
        print(f"📈 Успешность: {summary['success_rate']:.1f}%")
        print(f"⏱️ Время выполнения: {summary['total_duration']:.2f}с")
        print("="*60)
        
        if summary['failed'] > 0:
            print("\n❌ ПРОВАЛИВШИЕСЯ ТЕСТЫ:")
            for result in summary['results']:
                if not result['success']:
                    error = result.get('error', 'Неизвестная ошибка')
                    print(f"  • {result['test_name']}: {error}")
        
        if summary['passed'] > 0:
            print("\n✅ УСПЕШНЫЕ ТЕСТЫ:")
            for result in summary['results']:
                if result['success']:
                    duration = result.get('duration', 0)
                    print(f"  • {result['test_name']}: {duration:.2f}с")
        
        print("\n📄 Подробный отчет сохранен в logs/")
        print("="*60)

# === ПРОСТЫЕ КОМАНДЫ ===

async def quick_test():
    """Быстрый тест - только Mock Server."""
    logger.info("⚡ Быстрый тест Mock Server")
    
    launcher = OntoTestLauncher()
    
    try:
        # Запускаем только Mock Server
        if await launcher.start_mock_server():
            logger.info("✅ Mock Server работает")
            
            # Простая проверка
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get("http://localhost:8082/") as response:
                    result = await response.json()
                    print(f"📊 Mock Server статус: {result}")
            
            await asyncio.sleep(2)
        
    finally:
        launcher._cleanup()

async def full_test():
    """Полный тест со всеми компонентами."""
    launcher = OntoTestLauncher()
    exit_code = await launcher.run_full_test_cycle()
    sys.exit(exit_code)

# === ГЛАВНАЯ ФУНКЦИЯ ===

async def main():
    """Главная функция запуска."""
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "quick":
            await quick_test()
        elif command == "full":
            await full_test()
        else:
            print("❌ Неизвестная команда. Используйте: quick или full")
            sys.exit(1)
    else:
        # По умолчанию - полный тест
        await full_test()

if __name__ == "__main__":
    print("🚀 OntoBot Test Launcher")
    print("Доступные команды:")
    print("  python run_ontobot_tests.py quick  - быстрый тест Mock Server")
    print("  python run_ontobot_tests.py full   - полный тест (по умолчанию)")
    print()
    
    asyncio.run(main()) 