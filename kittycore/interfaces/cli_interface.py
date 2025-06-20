#!/usr/bin/env python3
"""
🎯 KittyCore 3.0 - CLI Интерфейс
Интерактивный командный интерфейс для работы с саморедуплицирующейся агентной системой
"""

import asyncio
import sys
from pathlib import Path
from typing import Optional
import signal

# Добавляем путь к kittycore
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from kittycore.core.unified_orchestrator import UnifiedOrchestrator, UnifiedConfig


class KittyCoreCliInterface:
    """🐱 Интерактивный CLI интерфейс для KittyCore 3.0"""
    
    def __init__(self):
        self.orchestrator: Optional[UnifiedOrchestrator] = None
        self.running = True
        
    async def initialize(self):
        """Инициализация системы"""
        print("🚀 Инициализация KittyCore 3.0...")
        
        config = UnifiedConfig(
            vault_path="./vault",
            enable_human_intervention=True,
            intervention_timeout=300
        )
        
        self.orchestrator = UnifiedOrchestrator(config)
        print("✅ KittyCore 3.0 готов к работе!")
        
    def print_banner(self):
        """Красивый баннер системы"""
        banner = """
╔══════════════════════════════════════════════════════════════╗
║                    🐱 KittyCore 3.0                         ║
║              Саморедуплицирующаяся агентная система          ║
║                                                              ║
║  🔄 Агенты создают агентов                                   ║
║  🧠 Коллективная память команды                              ║
║  📊 Граф-оркестрация процессов                               ║
║  🎯 Адаптивность под любые задачи                            ║
║  👤 Human-AI синергия                                        ║
║  🚀 Самообучение и эволюция                                  ║
╚══════════════════════════════════════════════════════════════╝
        """
        print(banner)
        
    def print_help(self):
        """Справка по командам"""
        help_text = """
📋 Доступные команды:

🎯 Основные:
  • Просто введите вашу задачу - система автоматически создаст агентов
  • help, h, ? - показать эту справку
  • exit, quit, q - выход из системы
  • clear, cls - очистить экран
  • status - показать статус системы

💡 Примеры задач:
  • "Создай сайт с котятами"
  • "Напиши скрипт для анализа данных"
  • "Сделай презентацию о ИИ"
  • "Создай API для управления задачами"
  • "Проанализируй файл data.csv"

🔥 Особенности:
  • Система сама определит сложность и создаст нужных агентов
  • Агенты будут координироваться через SharedChat
  • Результаты сохраняются в Obsidian vault
  • Качество проверяется революционной системой валидации
        """
        print(help_text)
        
    def print_status(self):
        """Статус системы"""
        if self.orchestrator:
            print("📊 Статус KittyCore 3.0:")
            print(f"  🗄️  Vault: {self.orchestrator.config.vault_path}")
            print(f"  🎯  SmartValidator: {'✅ Активен' if self.orchestrator.smart_validator else '❌ Отключен'}")
            print(f"  🧠  Самообучение: {'✅ Активно' if self.orchestrator.learning_system else '❌ Отключено'}")
            print(f"  🔍  Векторная память: {'✅ Активна' if self.orchestrator.vector_store else '❌ Отключена'}")
            print(f"  📊  Метрики: {'✅ Активны' if self.orchestrator.metrics_collector else '❌ Отключены'}")
            print(f"  💬  SharedChat: {'✅ Активен' if self.orchestrator.shared_chat else '❌ Отключен'}")
            print(f"  👤  Human-in-the-loop: {'✅ Активен' if self.orchestrator.human_intervention else '❌ Отключен'}")
        else:
            print("❌ Система не инициализирована")
            
    async def process_task(self, task: str) -> bool:
        """Обработка задачи пользователя"""
        if not self.orchestrator:
            print("❌ Система не инициализирована")
            return False
            
        print(f"\n🚀 Запускаю задачу: {task}")
        print("=" * 60)
        
        try:
            result = await self.orchestrator.solve_task(task)
            
            print("\n" + "=" * 60)
            print("🎉 ЗАДАЧА ЗАВЕРШЕНА!")
            print(f"📋 ID: {result['task_id']}")
            print(f"⏱️  Время: {result['duration']:.1f}с")
            print(f"🤖 Агентов: {result['agents_created']}")
            print(f"📁 Файлов: {len(result['created_files'])}")
            print(f"⭐ Качество: {result['validation']['quality_score']:.2f}")
            
            if result['created_files']:
                print(f"\n📂 Созданные файлы:")
                for file in result['created_files']:
                    print(f"  • {file}")
                    
            if result['validation']['issues']:
                print(f"\n⚠️  Проблемы:")
                for issue in result['validation']['issues']:
                    print(f"  • {issue}")
                    
            print(f"\n🗄️  Результаты сохранены в: {result['vault_path']}")
            return True
            
        except Exception as e:
            print(f"\n❌ Ошибка выполнения: {e}")
            return False
            
    async def run_interactive(self):
        """Основной интерактивный цикл"""
        self.print_banner()
        await self.initialize()
        self.print_help()
        
        while self.running:
            try:
                # Красивый промпт
                user_input = input("\n🐱 KittyCore> ").strip()
                
                if not user_input:
                    continue
                    
                # Обработка команд
                command = user_input.lower()
                
                if command in ['exit', 'quit', 'q']:
                    print("👋 До свидания! KittyCore 3.0 завершает работу...")
                    self.running = False
                    break
                    
                elif command in ['help', 'h', '?']:
                    self.print_help()
                    
                elif command in ['clear', 'cls']:
                    import os
                    os.system('clear' if os.name == 'posix' else 'cls')
                    self.print_banner()
                    
                elif command == 'status':
                    self.print_status()
                    
                else:
                    # Это задача для выполнения
                    await self.process_task(user_input)
                    
            except KeyboardInterrupt:
                print("\n\n⚠️  Получен сигнал прерывания (Ctrl+C)")
                confirm = input("❓ Действительно выйти? (y/n): ").strip().lower()
                if confirm in ['y', 'yes', 'да']:
                    self.running = False
                    break
                else:
                    print("▶️  Продолжаем работу...")
                    
            except EOFError:
                print("\n👋 До свидания!")
                self.running = False
                break
                
            except Exception as e:
                print(f"❌ Неожиданная ошибка: {e}")
                print("🔄 Система продолжает работу...")


def setup_signal_handlers(cli_interface):
    """Настройка обработчиков сигналов"""
    def signal_handler(signum, frame):
        print(f"\n⚠️  Получен сигнал {signum}")
        cli_interface.running = False
        
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


async def main():
    """Главная функция"""
    cli_interface = KittyCoreCliInterface()
    setup_signal_handlers(cli_interface)
    
    try:
        await cli_interface.run_interactive()
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main()) 