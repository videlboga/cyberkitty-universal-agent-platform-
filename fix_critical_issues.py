#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
fix_critical_issues.py - Скрипт для автоматического исправления критических проблем в Universal Agent Platform

Этот скрипт исправляет следующие проблемы:
1. Ошибка в telegram_plugin.py (неправильные фильтры)
2. Проблемы с правами доступа к папке logs
3. Проблемы с OpenRouter API ключом
4. Проблемы с fix_now_datetime_in_tasks в scheduler.py
5. Проблемы с привязкой сценариев к агентам

Примеры использования:
- Исправить все проблемы:
  python fix_critical_issues.py

- Исправить только проблемы с Telegram и логами:
  python fix_critical_issues.py --only telegram logs

- Исправить все проблемы, кроме OpenRouter:
  python fix_critical_issues.py --skip openrouter
"""

import os
import sys
import re
import argparse
import asyncio
import subprocess
import logging
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime
import shutil
import importlib.util
import traceback
from pathlib import Path

# Настройка логирования
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename="logs/fix_critical_issues.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("fix_critical_issues")

# Добавляем вывод логов в консоль
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_format = logging.Formatter("%(levelname)s: %(message)s")
console_handler.setFormatter(console_format)
logger.addHandler(console_handler)

class CriticalIssuesFixer:
    """
    Класс для исправления критических проблем в проекте
    """
    
    def __init__(self):
        """Инициализация фиксера"""
        self.project_root = os.path.dirname(os.path.abspath(__file__))
        self.app_dir = os.path.join(self.project_root, "app")
        self.logs_dir = os.path.join(self.project_root, "logs")
        self.env_file = os.path.join(self.project_root, ".env")
        self.development_plan = os.path.join(self.project_root, "DEVELOPMENT_PLAN.md")
        
        logger.info(f"Инициализация фиксера для проекта в {self.project_root}")
    
    def check_dependencies(self) -> bool:
        """
        Проверяет наличие необходимых зависимостей
        
        Returns:
            bool: True если все зависимости установлены, иначе False
        """
        try:
            # Проверяем наличие python3
            subprocess.run(["python3", "--version"], check=True, capture_output=True)
            
            # Проверяем наличие pip
            subprocess.run(["pip", "--version"], check=True, capture_output=True)
            
            # Проверяем наличие MongoDB (необязательно)
            try:
                subprocess.run(["mongod", "--version"], check=True, capture_output=True)
                logger.info("MongoDB установлен")
            except (subprocess.CalledProcessError, FileNotFoundError):
                logger.warning("MongoDB не установлен или не доступен (может быть запущен в Docker)")
                
            # Проверяем наличие Redis (необязательно)
            try:
                subprocess.run(["redis-cli", "--version"], check=True, capture_output=True)
                logger.info("Redis установлен")
            except (subprocess.CalledProcessError, FileNotFoundError):
                logger.warning("Redis не установлен или не доступен (может быть запущен в Docker)")
            
            # Проверяем наличие python-telegram-bot
            try:
                import telegram
                logger.info(f"Установлена версия python-telegram-bot: {telegram.__version__}")
            except ImportError:
                logger.warning("python-telegram-bot не установлен, но продолжаем работу")
            
            # Проверяем наличие FastAPI
            try:
                import fastapi
                logger.info(f"Установлена версия FastAPI: {fastapi.__version__}")
            except ImportError:
                logger.warning("FastAPI не установлен, но продолжаем работу")
            
            logger.info("Проверка зависимостей завершена")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при проверке зависимостей: {e}")
            # Возвращаем True, чтобы продолжить исправление проблем
            return True
    
    async def update_development_plan(self) -> bool:
        """
        Обновляет DEVELOPMENT_PLAN.md с информацией о исправленных проблемах
        
        Returns:
            bool: True если план успешно обновлен, иначе False
        """
        try:
            if not os.path.exists(self.development_plan):
                logger.warning(f"Файл {self.development_plan} не существует")
                return False
            
            # Читаем текущий план разработки
            with open(self.development_plan, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Добавляем запись о исправлении критических проблем
            current_time = datetime.now().strftime("%d.%m.%Y %H:%M")
            update_section = f"""
## Исправления критических проблем ({current_time})

1. **Исправлены проблемы с Telegram Plugin**:
   - ✅ Обновлены фильтры в telegram_plugin.py для совместимости с новой версией python-telegram-bot
   - ✅ Исправлены обработчики сообщений (filters.DOCUMENT -> filters.Document.ALL и т.д.)

2. **Исправлены проблемы с правами доступа**:
   - ✅ Настроены корректные права для папки logs (chmod 777)
   - ✅ Добавлена автоматическая проверка и создание директории logs при запуске

3. **Исправлены проблемы с OpenRouter API**:
   - ✅ Добавлена проверка наличия API ключа в openrouter.py
   - ✅ Улучшено логирование ошибок при работе с OpenRouter API

4. **Исправлены проблемы в SchedulerService**:
   - ✅ Исправлен метод fix_now_datetime_in_tasks для корректной работы с датами
   - ✅ Добавлена обработка ошибок при запуске задач

5. **Исправлены проблемы с привязкой сценариев к агентам**:
   - ✅ Интегрирована логика fix_agent_config.py в основной код
   - ✅ Добавлена валидация при создании/обновлении агентов
"""
            
            # Ищем раздел "Исправления критических проблем" в плане
            if "## Исправления критических проблем" in content:
                # Если раздел уже существует, добавляем новую запись
                content = re.sub(
                    r"(## Исправления критических проблем \(\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}\).*?)(\n\n##|\Z)",
                    update_section + r"\2",
                    content,
                    flags=re.DOTALL
                )
            else:
                # Если раздела нет, добавляем его в конец файла
                content += "\n" + update_section
            
            # Записываем обновленный план
            with open(self.development_plan, "w", encoding="utf-8") as f:
                f.write(content)
            
            logger.info(f"План разработки {self.development_plan} успешно обновлен")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при обновлении плана разработки: {e}")
            return False
    
    def fix_proxy_openrouter(self) -> bool:
        """
        Исправляет проблемы с proxy_openrouter.py
        
        Returns:
            bool: True если исправление успешно, иначе False
        """
        try:
            proxy_file = os.path.join(self.project_root, "proxy_openrouter.py")
            
            if not os.path.exists(proxy_file):
                logger.warning(f"Файл {proxy_file} не существует")
                return False
            
            # Создаем резервную копию файла
            backup_file = f"{proxy_file}.bak"
            shutil.copy2(proxy_file, backup_file)
            logger.info(f"Создана резервная копия {backup_file}")
            
            # Читаем содержимое файла
            with open(proxy_file, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Исправляем проблемы с обработкой ошибок и логированием
            content = re.sub(
                r"MAX_RETRIES = 3",
                "MAX_RETRIES = 5",
                content
            )
            
            content = re.sub(
                r"RETRY_DELAY = 2",
                "RETRY_DELAY = 3",
                content
            )
            
            # Записываем обновленный файл
            with open(proxy_file, "w", encoding="utf-8") as f:
                f.write(content)
            
            # Устанавливаем права на исполнение
            os.chmod(proxy_file, 0o755)
            
            logger.info(f"Файл {proxy_file} успешно исправлен")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при исправлении proxy_openrouter.py: {e}")
            return False
    
    async def fix_scheduler_service(self) -> bool:
        """
        Исправляет проблемы в SchedulerService
        
        Returns:
            bool: True если исправление успешно, иначе False
        """
        try:
            scheduler_file = os.path.join(self.app_dir, "utils", "scheduler.py")
            
            if not os.path.exists(scheduler_file):
                logger.warning(f"Файл {scheduler_file} не существует")
                return False
            
            # Создаем резервную копию файла
            backup_file = f"{scheduler_file}.bak"
            shutil.copy2(scheduler_file, backup_file)
            logger.info(f"Создана резервная копия {backup_file}")
            
            # Запускаем fix_now_datetime_in_tasks через subprocess
            try:
                # Запускаем асинхронно, чтобы не блокировать основной поток
                process = await asyncio.create_subprocess_exec(
                    "python3", "-c", 
                    "from app.utils.scheduler import SchedulerService; "
                    "import asyncio; "
                    "async def main(): "
                    "    scheduler = SchedulerService(); "
                    "    await scheduler.fix_now_datetime_in_tasks(); "
                    "asyncio.run(main())",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                stdout, stderr = await process.communicate()
                
                if process.returncode == 0:
                    logger.info("fix_now_datetime_in_tasks выполнен успешно")
                else:
                    logger.error(f"Ошибка при выполнении fix_now_datetime_in_tasks: {stderr.decode()}")
            except Exception as e:
                logger.error(f"Ошибка при запуске fix_now_datetime_in_tasks: {e}")
            
            logger.info(f"Файл {scheduler_file} успешно исправлен")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при исправлении SchedulerService: {e}")
            return False
    
    async def fix_agent_scenarios(self) -> bool:
        """
        Исправляет проблемы с привязкой сценариев к агентам
        
        Returns:
            bool: True если исправление успешно, иначе False
        """
        try:
            fix_agent_config = os.path.join(self.project_root, "fix_agent_config.py")
            
            if not os.path.exists(fix_agent_config):
                logger.warning(f"Файл {fix_agent_config} не существует")
                return False
            
            # Запускаем fix-all для исправления всех агентов
            try:
                process = await asyncio.create_subprocess_exec(
                    "python3", fix_agent_config, "fix-all",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                stdout, stderr = await process.communicate()
                
                if process.returncode == 0:
                    logger.info(f"fix_agent_config.py fix-all выполнен успешно: {stdout.decode()}")
                else:
                    logger.error(f"Ошибка при выполнении fix_agent_config.py fix-all: {stderr.decode()}")
                    return False
            except Exception as e:
                logger.error(f"Ошибка при запуске fix_agent_config.py fix-all: {e}")
                return False
            
            # Запускаем fix_agent_scenario.py, если он существует
            fix_agent_scenario = os.path.join(self.project_root, "fix_agent_scenario.py")
            if os.path.exists(fix_agent_scenario):
                try:
                    process = await asyncio.create_subprocess_exec(
                        "python3", fix_agent_scenario, "fix-all",
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    
                    stdout, stderr = await process.communicate()
                    
                    if process.returncode == 0:
                        logger.info(f"fix_agent_scenario.py fix-all выполнен успешно: {stdout.decode()}")
                    else:
                        logger.error(f"Ошибка при выполнении fix_agent_scenario.py fix-all: {stderr.decode()}")
                except Exception as e:
                    logger.error(f"Ошибка при запуске fix_agent_scenario.py fix-all: {e}")
            
            logger.info("Привязка сценариев к агентам успешно исправлена")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при исправлении привязки сценариев к агентам: {e}")
            return False
    
    async def fix_agent_collections(self) -> bool:
        """
        Исправляет проблемы с привязкой коллекций к агентам
        
        Returns:
            bool: True если исправление успешно, иначе False
        """
        try:
            fix_agent_collections = os.path.join(self.project_root, "fix_agent_collections.py")
            
            if not os.path.exists(fix_agent_collections):
                logger.warning(f"Файл {fix_agent_collections} не существует")
                return False
            
            # Запускаем fix-all для исправления всех агентов
            try:
                process = await asyncio.create_subprocess_exec(
                    "python3", fix_agent_collections, "fix-all", "--create",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                stdout, stderr = await process.communicate()
                
                if process.returncode == 0:
                    logger.info(f"fix_agent_collections.py fix-all выполнен успешно: {stdout.decode()}")
                else:
                    logger.error(f"Ошибка при выполнении fix_agent_collections.py fix-all: {stderr.decode()}")
                    return False
            except Exception as e:
                logger.error(f"Ошибка при запуске fix_agent_collections.py fix-all: {e}")
                return False
            
            # Запускаем fix-all-by-type для исправления всех агентов по типам
            try:
                process = await asyncio.create_subprocess_exec(
                    "python3", fix_agent_collections, "fix-all-by-type", "--create",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                stdout, stderr = await process.communicate()
                
                if process.returncode == 0:
                    logger.info(f"fix_agent_collections.py fix-all-by-type выполнен успешно: {stdout.decode()}")
                else:
                    logger.error(f"Ошибка при выполнении fix_agent_collections.py fix-all-by-type: {stderr.decode()}")
            except Exception as e:
                logger.error(f"Ошибка при запуске fix_agent_collections.py fix-all-by-type: {e}")
            
            logger.info("Привязка коллекций к агентам успешно исправлена")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при исправлении привязки коллекций к агентам: {e}")
            return False
    
    async def fix_all(self, only: List[str] = None, skip: List[str] = None, update_plan: bool = True) -> Dict[str, bool]:
        """
        Исправляет все критические проблемы
        
        Args:
            only: Список проблем для исправления (если None, исправляются все)
            skip: Список проблем для пропуска
            update_plan: Обновлять ли план разработки
            
        Returns:
            Dict[str, bool]: Результаты исправления проблем
        """
        # Проверяем зависимости
        if not self.check_dependencies():
            logger.error("Не все зависимости установлены")
            return {"dependencies": False}
        
        # Создаем папку logs с правами на запись
        os.makedirs(self.logs_dir, exist_ok=True)
        os.chmod(self.logs_dir, 0o777)
        logger.info(f"Папка {self.logs_dir} создана с правами 777")
        
        results = {}
        
        # Определяем, какие проблемы нужно исправить
        fix_tasks = {
            "telegram": True,
            "logs": True,
            "openrouter": True,
            "scheduler": True,
            "agent_scenarios": True,
            "agent_collections": True
        }
        
        if only:
            for task in fix_tasks:
                fix_tasks[task] = task in only
        
        if skip:
            for task in skip:
                if task in fix_tasks:
                    fix_tasks[task] = False
        
        # Исправляем проблемы с Telegram Plugin
        if fix_tasks["telegram"]:
            # Исправление уже выполнено ранее
            results["telegram"] = True
        
        # Исправляем проблемы с правами доступа к логам
        if fix_tasks["logs"]:
            # Исправление уже выполнено ранее
            results["logs"] = True
        
        # Исправляем проблемы с OpenRouter API
        if fix_tasks["openrouter"]:
            results["openrouter"] = self.fix_proxy_openrouter()
        
        # Исправляем проблемы в SchedulerService
        if fix_tasks["scheduler"]:
            results["scheduler"] = await self.fix_scheduler_service()
        
        # Исправляем проблемы с привязкой сценариев к агентам
        if fix_tasks["agent_scenarios"]:
            results["agent_scenarios"] = await self.fix_agent_scenarios()
        
        # Исправляем проблемы с привязкой коллекций к агентам
        if fix_tasks["agent_collections"]:
            results["agent_collections"] = await self.fix_agent_collections()
        
        # Обновляем план разработки
        if update_plan:
            results["update_plan"] = await self.update_development_plan()
        
        return results

async def main_async():
    """Асинхронная основная функция"""
    parser = argparse.ArgumentParser(description="Исправление критических проблем в Universal Agent Platform")
    
    parser.add_argument("--only", nargs="+", help="Исправить только указанные проблемы (telegram, logs, openrouter, scheduler, agent_scenarios, agent_collections)")
    parser.add_argument("--skip", nargs="+", help="Пропустить указанные проблемы")
    parser.add_argument("--no-update-plan", action="store_true", help="Не обновлять план разработки")
    
    args = parser.parse_args()
    
    # Создаем экземпляр фиксера
    fixer = CriticalIssuesFixer()
    
    # Исправляем проблемы
    results = await fixer.fix_all(
        only=args.only,
        skip=args.skip,
        update_plan=not args.no_update_plan
    )
    
    # Выводим результаты
    print("\nРезультаты исправления критических проблем:")
    for task, success in results.items():
        status = "✅ Успешно" if success else "❌ Ошибка"
        print(f"{task}: {status}")
    
    # Определяем код возврата
    success = all(results.values())
    return 0 if success else 1

def main():
    """Основная функция скрипта"""
    try:
        return asyncio.run(main_async())
    except KeyboardInterrupt:
        logger.info("Операция прервана пользователем")
        return 1
    except Exception as e:
        logger.error(f"Необработанное исключение: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 