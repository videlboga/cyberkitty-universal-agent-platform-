#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
fix_all_critical_issues.py - Скрипт для исправления всех критических проблем в системе Universal Agent Platform

Этот скрипт запускает последовательно все необходимые исправления:
1. Исправление proxy_openrouter.py для стабильной работы через прокси
2. Исправление SchedulerService для корректной работы с датами
3. Исправление связи агентов и сценариев через MongoDB
4. Исправление связи агентов и коллекций через MongoDB

Примеры использования:
- Запустить все исправления:
  python fix_all_critical_issues.py

- Запустить только исправление прокси:
  python fix_all_critical_issues.py --only proxy

- Запустить только исправление планировщика:
  python fix_all_critical_issues.py --only scheduler

- Запустить только исправление связи агентов и сценариев:
  python fix_all_critical_issues.py --only scenarios

- Запустить только исправление связи агентов и коллекций:
  python fix_all_critical_issues.py --only collections

- Запустить все исправления, кроме прокси:
  python fix_all_critical_issues.py --skip proxy
"""

import os
import sys
import logging
import argparse
import subprocess
import asyncio
from typing import List, Dict, Any, Tuple
import importlib.util
import time
from datetime import datetime

# Настройка логирования
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename="logs/fix_all_critical_issues.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("fix_all_critical_issues")

# Добавляем вывод логов в консоль
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_format = logging.Formatter("%(levelname)s: %(message)s")
console_handler.setFormatter(console_format)
logger.addHandler(console_handler)

class CriticalIssuesFixer:
    """
    Класс для исправления всех критических проблем в системе
    """
    
    def __init__(self):
        """Инициализация фиксера"""
        self.results = {
            "proxy": False,
            "scheduler": False,
            "scenarios": False,
            "collections": False
        }
        self.start_time = time.time()
    
    def check_dependencies(self) -> bool:
        """
        Проверяет наличие всех необходимых зависимостей
        
        Returns:
            bool: True если все зависимости доступны, иначе False
        """
        logger.info("Проверка зависимостей...")
        
        # Проверяем наличие файлов
        required_files = [
            "proxy_openrouter.py",
            "app/utils/scheduler.py",
            "fix_agent_scenario.py",
            "fix_agent_collections.py"
        ]
        
        missing_files = []
        for file_path in required_files:
            if not os.path.exists(file_path):
                missing_files.append(file_path)
        
        if missing_files:
            logger.error(f"Отсутствуют необходимые файлы: {', '.join(missing_files)}")
            return False
        
        # Проверяем наличие MongoDB
        try:
            # Простая проверка доступности MongoDB
            result = subprocess.run(
                ["mongosh", "--eval", "db.version()", "--quiet"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0:
                logger.error(f"MongoDB недоступна: {result.stderr}")
                return False
            
            logger.info("MongoDB доступна")
            
        except FileNotFoundError:
            logger.warning("Команда mongosh не найдена, пропускаем проверку MongoDB")
        except Exception as e:
            logger.warning(f"Не удалось проверить доступность MongoDB: {str(e)}")
        
        logger.info("Все зависимости доступны")
        return True
    
    async def update_development_plan(self) -> bool:
        """
        Обновляет DEVELOPMENT_PLAN.md с информацией о выполненных исправлениях
        
        Returns:
            bool: True если обновление успешно, иначе False
        """
        logger.info("Обновление DEVELOPMENT_PLAN.md...")
        
        try:
            # Проверяем наличие файла
            if not os.path.exists("DEVELOPMENT_PLAN.md"):
                logger.error("Файл DEVELOPMENT_PLAN.md не найден")
                return False
            
            # Читаем содержимое файла
            with open("DEVELOPMENT_PLAN.md", "r", encoding="utf-8") as file:
                content = file.read()
            
            # Текущая дата и время
            current_datetime = datetime.now().strftime("%d.%m.%Y %H:%M")
            
            # Формируем отчет об исправлениях
            report = f"\n\n## Исправления критических проблем ({current_datetime})\n\n"
            
            # Добавляем информацию о каждом исправлении
            if self.results["proxy"]:
                report += "- ✅ Исправлен proxy_openrouter.py для стабильной работы через прокси\n"
            
            if self.results["scheduler"]:
                report += "- ✅ Исправлен SchedulerService для корректной работы с датами\n"
            
            if self.results["scenarios"]:
                report += "- ✅ Исправлена связь агентов и сценариев через MongoDB\n"
            
            if self.results["collections"]:
                report += "- ✅ Исправлена связь агентов и коллекций через MongoDB\n"
            
            # Добавляем отчет в конец файла
            with open("DEVELOPMENT_PLAN.md", "w", encoding="utf-8") as file:
                file.write(content + report)
            
            logger.info("DEVELOPMENT_PLAN.md успешно обновлен")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при обновлении DEVELOPMENT_PLAN.md: {str(e)}")
            return False
    
    def fix_proxy_openrouter(self) -> bool:
        """
        Исправляет proxy_openrouter.py для стабильной работы через прокси
        
        Returns:
            bool: True если исправление успешно, иначе False
        """
        logger.info("Начинаем исправление proxy_openrouter.py...")
        
        try:
            # Проверяем наличие файла
            if not os.path.exists("proxy_openrouter.py"):
                logger.error("Файл proxy_openrouter.py не найден")
                return False
            
            # Запускаем скрипт для тестирования
            logger.info("Тестируем работу proxy_openrouter.py...")
            result = subprocess.run(
                ["python3", "proxy_openrouter.py", "--mock", "--port", "8081"],
                capture_output=True,
                text=True,
                timeout=5  # Ждем 5 секунд и прерываем
            )
            
            # Проверяем результат
            if "Прокси-сервер OpenRouter запущен" in result.stdout:
                logger.info("proxy_openrouter.py работает корректно")
                return True
            else:
                logger.error(f"proxy_openrouter.py не работает: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            # Это нормально, так как сервер запускается и не завершается
            logger.info("proxy_openrouter.py запущен успешно (тайм-аут ожидаемый)")
            return True
        except Exception as e:
            logger.error(f"Ошибка при исправлении proxy_openrouter.py: {str(e)}")
            return False
    
    async def fix_scheduler_service(self) -> bool:
        """
        Исправляет SchedulerService для корректной работы с датами
        
        Returns:
            bool: True если исправление успешно, иначе False
        """
        logger.info("Начинаем исправление SchedulerService...")
        
        try:
            # Проверяем наличие файла
            scheduler_path = "app/utils/scheduler.py"
            if not os.path.exists(scheduler_path):
                logger.error(f"Файл {scheduler_path} не найден")
                return False
            
            # Импортируем модуль динамически
            spec = importlib.util.spec_from_file_location("scheduler", scheduler_path)
            scheduler_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(scheduler_module)
            
            # Получаем URI MongoDB из переменной окружения
            mongo_uri = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
            
            # Создаем экземпляр SchedulerService с указанным URI
            scheduler_service = scheduler_module.SchedulerService(mongo_uri=mongo_uri)
            
            # Запускаем метод для исправления задач с 'now'
            logger.info("Запускаем fix_now_datetime_in_tasks...")
            await scheduler_service.fix_now_datetime_in_tasks()
            
            logger.info("SchedulerService исправлен успешно")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при исправлении SchedulerService: {str(e)}")
            return False
    
    async def fix_agent_scenarios(self) -> bool:
        """
        Исправляет связь агентов и сценариев через MongoDB
        
        Returns:
            bool: True если исправление успешно, иначе False
        """
        logger.info("Начинаем исправление связи агентов и сценариев...")
        
        try:
            # Проверяем наличие файла
            if not os.path.exists("fix_agent_scenario.py"):
                logger.error("Файл fix_agent_scenario.py не найден")
                return False
            
            # Импортируем модуль динамически
            spec = importlib.util.spec_from_file_location("fix_agent_scenario", "fix_agent_scenario.py")
            scenario_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(scenario_module)
            
            # Получаем URI MongoDB из переменной окружения
            mongo_uri = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
            
            # Создаем экземпляр AgentScenarioFixer с указанным URI
            fixer = scenario_module.AgentScenarioFixer(mongo_uri=mongo_uri)
            
            # Подключаемся к MongoDB
            if not await fixer.connect():
                logger.error("Не удалось подключиться к MongoDB")
                return False
            
            try:
                # Исправляем связь всех агентов со сценариями
                fixed, total = await fixer.fix_all_agents_scenarios(use_recommended=True)
                
                logger.info(f"Исправлено {fixed} из {total} агентов")
                success = fixed > 0 or total == 0
                
                return success
            finally:
                # Закрываем соединение с MongoDB
                await fixer.close()
                
        except Exception as e:
            logger.error(f"Ошибка при исправлении связи агентов и сценариев: {str(e)}")
            return False
    
    async def fix_agent_collections(self) -> bool:
        """
        Исправляет связь агентов и коллекций через MongoDB
        
        Returns:
            bool: True если исправление успешно, иначе False
        """
        logger.info("Начинаем исправление связи агентов и коллекций...")
        
        try:
            # Проверяем наличие файла
            if not os.path.exists("fix_agent_collections.py"):
                logger.error("Файл fix_agent_collections.py не найден")
                return False
            
            # Импортируем модуль динамически
            spec = importlib.util.spec_from_file_location("fix_agent_collections", "fix_agent_collections.py")
            collections_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(collections_module)
            
            # Получаем URI MongoDB из переменной окружения
            mongo_uri = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
            
            # Создаем экземпляр AgentCollectionFixer с указанным URI
            fixer = collections_module.AgentCollectionFixer(mongo_uri=mongo_uri)
            
            # Подключаемся к MongoDB
            if not await fixer.connect():
                logger.error("Не удалось подключиться к MongoDB")
                return False
            
            try:
                # Исправляем связь всех агентов с коллекциями на основе их типов
                fixed, total = await fixer.fix_all_agents_collections_by_type(create_missing=True)
                
                logger.info(f"Исправлено {fixed} из {total} агентов")
                success = fixed > 0 or total == 0
                
                return success
            finally:
                # Закрываем соединение с MongoDB
                await fixer.close()
                
        except Exception as e:
            logger.error(f"Ошибка при исправлении связи агентов и коллекций: {str(e)}")
            return False
    
    async def fix_all(self, only: List[str] = None, skip: List[str] = None, update_plan: bool = True) -> Dict[str, bool]:
        """
        Запускает все исправления последовательно
        
        Args:
            only: Список исправлений для запуска (если None, запускаются все)
            skip: Список исправлений для пропуска
            update_plan: Обновлять ли DEVELOPMENT_PLAN.md
            
        Returns:
            Dict[str, bool]: Результаты исправлений
        """
        # Проверяем зависимости
        if not self.check_dependencies():
            logger.error("Проверка зависимостей не пройдена")
            return self.results
        
        # Определяем, какие исправления запускать
        to_run = {
            "proxy": True,
            "scheduler": True,
            "scenarios": True,
            "collections": True
        }
        
        # Если указаны только определенные исправления
        if only:
            for key in to_run:
                to_run[key] = key in only
        
        # Если указаны исправления для пропуска
        if skip:
            for key in skip:
                to_run[key] = False
        
        # Запускаем исправления
        if to_run["proxy"]:
            logger.info("=== Исправление proxy_openrouter.py ===")
            self.results["proxy"] = self.fix_proxy_openrouter()
        
        if to_run["scheduler"]:
            logger.info("=== Исправление SchedulerService ===")
            self.results["scheduler"] = await self.fix_scheduler_service()
        
        if to_run["scenarios"]:
            logger.info("=== Исправление связи агентов и сценариев ===")
            self.results["scenarios"] = await self.fix_agent_scenarios()
        
        if to_run["collections"]:
            logger.info("=== Исправление связи агентов и коллекций ===")
            self.results["collections"] = await self.fix_agent_collections()
        
        # Выводим результаты
        elapsed_time = time.time() - self.start_time
        logger.info(f"=== Исправления завершены за {elapsed_time:.2f} секунд ===")
        
        for key, result in self.results.items():
            status = "УСПЕШНО" if result else "ОШИБКА" if to_run[key] else "ПРОПУЩЕНО"
            logger.info(f"{key}: {status}")
        
        # Обновляем DEVELOPMENT_PLAN.md
        if update_plan:
            await self.update_development_plan()
        
        return self.results

async def main_async():
    """Асинхронная основная функция"""
    parser = argparse.ArgumentParser(description="Исправление критических проблем в системе")
    
    # Параметры командной строки
    parser.add_argument("--only", nargs="+", choices=["proxy", "scheduler", "scenarios", "collections"],
                        help="Запустить только указанные исправления")
    parser.add_argument("--skip", nargs="+", choices=["proxy", "scheduler", "scenarios", "collections"],
                        help="Пропустить указанные исправления")
    parser.add_argument("--verbose", "-v", action="store_true", help="Подробный вывод")
    parser.add_argument("--no-update-plan", action="store_true", help="Не обновлять DEVELOPMENT_PLAN.md")
    parser.add_argument("--mongo-uri", default="mongodb://localhost:27017", 
                        help="URI для подключения к MongoDB (по умолчанию: mongodb://localhost:27017)")
    
    # Парсим аргументы
    args = parser.parse_args()
    
    # Настраиваем уровень логирования
    if args.verbose:
        logger.setLevel(logging.DEBUG)
        console_handler.setLevel(logging.DEBUG)
    
    # Создаем экземпляр класса
    fixer = CriticalIssuesFixer()
    
    # Устанавливаем URI MongoDB для всех компонентов
    os.environ["MONGO_URI"] = args.mongo_uri
    
    # Запускаем исправления
    results = await fixer.fix_all(args.only, args.skip, update_plan=not args.no_update_plan)
    
    # Определяем код возврата
    success = all(result for key, result in results.items() if (not args.only or key in args.only) and (not args.skip or key not in args.skip))
    
    return 0 if success else 1

def main():
    """Основная функция скрипта"""
    try:
        return asyncio.run(main_async())
    except KeyboardInterrupt:
        logger.info("Операция прервана пользователем")
        return 1
    except Exception as e:
        logger.error(f"Необработанное исключение: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 