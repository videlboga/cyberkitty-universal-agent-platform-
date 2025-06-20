#!/usr/bin/env python3
"""
🔧 ИСПРАВЛЕННЫЙ РЕАЛЬНЫЙ ТЕСТ ИНСТРУМЕНТОВ KITTYCORE 3.0
Правильные API каждого инструмента без моков!
"""

import sys
import asyncio
import json
import time
from pathlib import Path
from typing import Dict, List, Any

# Добавляем путь к KittyCore
sys.path.append(str(Path(__file__).parent / 'kittycore'))

class FixedToolsTester:
    def __init__(self):
        self.results = []
        self.memory_records = []
        self.missing_keys = []
        
    async def test_api_request_tool(self):
        """Тест ApiRequestTool - работает!"""
        from kittycore.tools import ApiRequestTool
        
        start_time = time.time()
        try:
            tool = ApiRequestTool()
            result = tool.execute(url="https://httpbin.org/get", method="GET")
            execution_time = time.time() - start_time
            
            if result.success:
                response_size = len(str(result.data))
                notes = f"✅ Время: {execution_time:.1f}с, размер: {response_size} байт"
                success = True
                
                self.memory_records.append({
                    "tool": "api_request_tool",
                    "working_action": "request",
                    "correct_params": {"url": "string", "method": "GET|POST|PUT|DELETE"},
                    "notes": notes,
                    "success": True
                })
            else:
                notes = f"❌ Ошибка: {result.error}"
                success = False
                
        except Exception as e:
            execution_time = time.time() - start_time
            notes = f"❌ Исключение: {str(e)[:100]}"
            success = False
            
        self.results.append({
            "tool": "api_request_tool",
            "success": success,
            "notes": notes,
            "execution_time": execution_time
        })
        
        print(f"🔧 api_request_tool: {notes}")
    
    async def test_super_system_tool(self):
        """Тест SuperSystemTool с правильными действиями"""
        from kittycore.tools import SuperSystemTool
        
        start_time = time.time()
        try:
            tool = SuperSystemTool()
            result = tool.execute(action="get_system_info")  # Правильное действие
            execution_time = time.time() - start_time
            
            if result.success:
                response_size = len(str(result.data))
                notes = f"✅ Время: {execution_time:.1f}с, размер: {response_size} байт"
                success = True
                
                self.memory_records.append({
                    "tool": "super_system_tool",
                    "working_action": "get_system_info",
                    "correct_params": {"action": "get_system_info|get_processes|get_resource_usage"},
                    "notes": notes,
                    "success": True
                })
            else:
                notes = f"❌ Ошибка: {result.error}"
                success = False
                
        except Exception as e:
            execution_time = time.time() - start_time
            notes = f"❌ Исключение: {str(e)[:100]}"
            success = False
            
        self.results.append({
            "tool": "super_system_tool",
            "success": success,
            "notes": notes,
            "execution_time": execution_time
        })
        
        print(f"🔧 super_system_tool: {notes}")
    
    async def test_computer_use_tool(self):
        """Тест ComputerUseTool"""
        from kittycore.tools import ComputerUseTool
        
        start_time = time.time()
        try:
            tool = ComputerUseTool()
            # ComputerUseTool не принимает action в execute()
            result = tool.take_screenshot()
            execution_time = time.time() - start_time
            
            if result.success:
                response_size = len(str(result.data))
                notes = f"✅ Время: {execution_time:.1f}с, размер: {response_size} байт"
                success = True
                
                self.memory_records.append({
                    "tool": "computer_use_tool",
                    "working_action": "take_screenshot",
                    "correct_params": {"method": "take_screenshot()"},
                    "notes": notes,
                    "success": True
                })
            else:
                notes = f"❌ Ошибка: {result.error}"
                success = False
                
        except Exception as e:
            execution_time = time.time() - start_time
            notes = f"❌ Исключение: {str(e)[:100]}"
            success = False
            
        self.results.append({
            "tool": "computer_use_tool",
            "success": success,
            "notes": notes,
            "execution_time": execution_time
        })
        
        print(f"🔧 computer_use_tool: {notes}")
    
    async def test_database_tool(self):
        """Тест DatabaseTool с правильными параметрами"""
        from kittycore.tools import DatabaseTool
        
        start_time = time.time()
        try:
            tool = DatabaseTool()
            # DatabaseTool требует query в execute()
            result = tool.execute("SELECT 1 as test")  # Простой тестовый запрос
            execution_time = time.time() - start_time
            
            if result.success:
                response_size = len(str(result.data))
                notes = f"✅ Время: {execution_time:.1f}с, размер: {response_size} байт"
                success = True
                
                self.memory_records.append({
                    "tool": "database_tool",
                    "working_action": "execute_query",
                    "correct_params": {"query": "SQL string"},
                    "notes": notes,
                    "success": True
                })
            else:
                notes = f"❌ Ошибка: {result.error}"
                success = False
                
        except Exception as e:
            execution_time = time.time() - start_time
            notes = f"❌ Исключение: {str(e)[:100]}"
            success = False
            
            # Проверяем на отсутствие database
            if "database" in str(e).lower() or "connection" in str(e).lower():
                self.missing_keys.append({
                    "tool": "database_tool",
                    "error": str(e),
                    "likely_missing_key": "DATABASE_URL или настройки подключения к БД"
                })
            
        self.results.append({
            "tool": "database_tool",
            "success": success,
            "notes": notes,
            "execution_time": execution_time
        })
        
        print(f"🔧 database_tool: {notes}")
    
    async def test_email_tool(self):
        """Тест EmailTool с правильными параметрами"""
        from kittycore.tools import EmailTool
        
        start_time = time.time()
        try:
            tool = EmailTool()
            # EmailTool требует to, subject, body
            result = tool.execute(
                to="test@example.com",
                subject="Тест KittyCore", 
                body="Тестовое письмо"
            )
            execution_time = time.time() - start_time
            
            if result.success:
                response_size = len(str(result.data))
                notes = f"✅ Время: {execution_time:.1f}с, размер: {response_size} байт"
                success = True
                
                self.memory_records.append({
                    "tool": "email_tool",
                    "working_action": "send_email",
                    "correct_params": {"to": "string", "subject": "string", "body": "string"},
                    "notes": notes,
                    "success": True
                })
            else:
                notes = f"❌ Ошибка: {result.error}"
                success = False
                
        except Exception as e:
            execution_time = time.time() - start_time
            notes = f"❌ Исключение: {str(e)[:100]}"
            success = False
            
            # Проверяем на отсутствие email настроек
            if any(word in str(e).lower() for word in ["smtp", "email", "password", "auth"]):
                self.missing_keys.append({
                    "tool": "email_tool",
                    "error": str(e),
                    "likely_missing_key": "EMAIL_PASSWORD, SMTP_SERVER или email настройки"
                })
            
        self.results.append({
            "tool": "email_tool",
            "success": success,
            "notes": notes,
            "execution_time": execution_time
        })
        
        print(f"🔧 email_tool: {notes}")
    
    async def test_telegram_tool(self):
        """Тест TelegramTool"""
        from kittycore.tools import TelegramTool
        
        start_time = time.time()
        try:
            tool = TelegramTool()
            result = tool.execute(
                chat_id="@test_channel",
                message="Тест KittyCore"
            )
            execution_time = time.time() - start_time
            
            if result.success:
                response_size = len(str(result.data))
                notes = f"✅ Время: {execution_time:.1f}с, размер: {response_size} байт"
                success = True
                
                self.memory_records.append({
                    "tool": "telegram_tool",
                    "working_action": "send_message",
                    "correct_params": {"chat_id": "string", "message": "string"},
                    "notes": notes,
                    "success": True
                })
            else:
                notes = f"❌ Ошибка: {result.error}"
                success = False
                
        except Exception as e:
            execution_time = time.time() - start_time
            notes = f"❌ Исключение: {str(e)[:100]}"
            success = False
            
            # Проверяем на отсутствие Telegram настроек
            if any(word in str(e).lower() for word in ["telegram", "bot", "token", "pyrogram"]):
                self.missing_keys.append({
                    "tool": "telegram_tool",
                    "error": str(e),
                    "likely_missing_key": "TELEGRAM_BOT_TOKEN + pip install pyrogram"
                })
            
        self.results.append({
            "tool": "telegram_tool",
            "success": success,
            "notes": notes,
            "execution_time": execution_time
        })
        
        print(f"🔧 telegram_tool: {notes}")
    
    async def test_ai_integration_tool(self):
        """Тест AIIntegrationTool - проверяем async"""
        from kittycore.tools import AIIntegrationTool
        
        start_time = time.time()
        try:
            tool = AIIntegrationTool()
            # Проверяем правильный async вызов
            result = await tool.execute(action="list_models")
            execution_time = time.time() - start_time
            
            if result.success:
                response_size = len(str(result.data))
                notes = f"✅ Время: {execution_time:.1f}с, размер: {response_size} байт"
                success = True
                
                self.memory_records.append({
                    "tool": "ai_integration_tool",
                    "working_action": "list_models",
                    "correct_params": {"action": "list_models"},
                    "notes": notes,
                    "success": True
                })
            else:
                notes = f"❌ Ошибка: {result.error}"
                success = False
                
        except Exception as e:
            execution_time = time.time() - start_time
            notes = f"❌ Исключение: {str(e)[:100]}"
            success = False
            
            # Проверяем на отсутствие API ключей
            if any(word in str(e).lower() for word in ["api", "key", "token", "openrouter"]):
                self.missing_keys.append({
                    "tool": "ai_integration_tool",
                    "error": str(e),
                    "likely_missing_key": "OPENROUTER_API_KEY"
                })
            
        self.results.append({
            "tool": "ai_integration_tool",
            "success": success,
            "notes": notes,
            "execution_time": execution_time
        })
        
        print(f"🔧 ai_integration_tool: {notes}")
        
    async def run_fixed_tests(self):
        """Запуск исправленных тестов"""
        
        print("🔧 ИСПРАВЛЕННЫЙ РЕАЛЬНЫЙ ТЕСТ ИНСТРУМЕНТОВ KITTYCORE 3.0")
        print("=" * 70)
        print("✅ Правильные API каждого инструмента")
        print("🚫 Без моков, только реальные вызовы")
        print()
        
        # Запускаем тесты
        await self.test_api_request_tool()
        await self.test_super_system_tool()
        await self.test_computer_use_tool()
        await self.test_database_tool()
        await self.test_email_tool()
        await self.test_telegram_tool()
        await self.test_ai_integration_tool()
        
        # Результаты
        self._print_results()
        self._save_results()
    
    def _print_results(self):
        """Вывод результатов"""
        
        print("\n" + "=" * 70)
        print("📊 РЕЗУЛЬТАТЫ ИСПРАВЛЕННОГО ТЕСТИРОВАНИЯ")
        print("=" * 70)
        
        total_tests = len(self.results)
        successful_tests = len([r for r in self.results if r["success"]])
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"🎯 Общий успех: {successful_tests}/{total_tests} = {success_rate:.1f}%")
        
        # Успешные
        successful = [r for r in self.results if r["success"]]
        if successful:
            print(f"\n✅ РАБОТАЮЩИЕ ИНСТРУМЕНТЫ ({len(successful)}):")
            for result in successful:
                print(f"   🔧 {result['tool']}: {result['notes']}")
        
        # Проблемные
        failed = [r for r in self.results if not r["success"]]
        if failed:
            print(f"\n❌ ПРОБЛЕМНЫЕ ИНСТРУМЕНТЫ ({len(failed)}):")
            for result in failed:
                print(f"   🔧 {result['tool']}: {result['notes']}")
        
        # Отсутствующие ключи
        if self.missing_keys:
            print(f"\n🔑 ОТСУТСТВУЮЩИЕ API КЛЮЧИ ({len(self.missing_keys)}):")
            for missing in self.missing_keys:
                print(f"   🔧 {missing['tool']}: {missing['likely_missing_key']}")
    
    def _save_results(self):
        """Сохранение результатов"""
        
        Path("test_tools_fixed_api").mkdir(exist_ok=True)
        
        # Детальные результаты
        with open("test_tools_fixed_api/results.json", 'w', encoding='utf-8') as f:
            json.dump({
                "summary": {
                    "total_tests": len(self.results),
                    "successful_tests": len([r for r in self.results if r["success"]]),
                    "success_rate": (len([r for r in self.results if r["success"]]) / len(self.results) * 100) if self.results else 0
                },
                "results": self.results,
                "missing_keys": self.missing_keys
            }, f, ensure_ascii=False, indent=2)
        
        # Записи для памяти
        with open("test_tools_fixed_api/memory_records.json", 'w', encoding='utf-8') as f:
            json.dump(self.memory_records, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 Результаты сохранены в test_tools_fixed_api/")

async def main():
    """Главная функция"""
    tester = FixedToolsTester()
    await tester.run_fixed_tests()

if __name__ == "__main__":
    asyncio.run(main()) 