#!/usr/bin/env python3
"""
🎯 ФИНАЛЬНЫЙ COMPREHENSIVE ТЕСТ ВСЕХ ИНСТРУМЕНТОВ KITTYCORE 3.0
Все правильные API, максимальный охват, без моков!
"""

import sys
import asyncio
import json
import time
from pathlib import Path
from typing import Dict, List, Any

# Добавляем путь к KittyCore
sys.path.append(str(Path(__file__).parent / 'kittycore'))

class FinalComprehensiveTester:
    def __init__(self):
        self.results = []
        self.memory_records = []
        self.missing_keys = []
        
    async def test_all_tools(self):
        """Тест всех инструментов с правильными API"""
        
        print("🎯 ФИНАЛЬНЫЙ COMPREHENSIVE ТЕСТ ВСЕХ ИНСТРУМЕНТОВ KITTYCORE 3.0")
        print("=" * 80)
        print("🚀 Максимальный охват с правильными API")
        print("🚫 Без моков, только реальные вызовы")
        print()
        
        # 1. API Request Tool ✅
        await self._test_tool("api_request_tool", self._test_api_request)
        
        # 2. Super System Tool ✅  
        await self._test_tool("super_system_tool", self._test_super_system)
        
        # 3. Email Tool ✅
        await self._test_tool("email_tool", self._test_email)
        
        # 4. Computer Use Tool (исправленный)
        await self._test_tool("computer_use_tool", self._test_computer_use)
        
        # 5. Database Tool (исправленный async)
        await self._test_tool("database_tool", self._test_database)
        
        # 6. AI Integration Tool (исправленный)
        await self._test_tool("ai_integration_tool", self._test_ai_integration)
        
        # 7. Security Tool 
        await self._test_tool("security_tool", self._test_security)
        
        # 8. Smart Function Tool
        await self._test_tool("smart_function_tool", self._test_smart_function)
        
        # 9. Vector Search Tool
        await self._test_tool("vector_search_tool", self._test_vector_search)
        
        # 10. Image Generation Tool
        await self._test_tool("image_generation_tool", self._test_image_generation)
        
        # 11. Document Tool
        await self._test_tool("document_tool", self._test_document)
        
        # 12. Enhanced Web Scraping Tool
        await self._test_tool("enhanced_web_scraping_tool", self._test_web_scraping)
        
        # 13. Web Client Tool
        await self._test_tool("web_client_tool", self._test_web_client)
        
        # 14. Telegram Tool (установка зависимостей)
        await self._test_tool("telegram_tool", self._test_telegram)
        
        # Результаты
        self._print_results()
        self._save_results()
    
    async def _test_tool(self, tool_name: str, test_func):
        """Универсальная обёртка для тестирования"""
        print(f"🔧 Тестирую {tool_name}...")
        
        start_time = time.time()
        try:
            result = await test_func()
            execution_time = time.time() - start_time
            
            if result.get("success", False):
                response_size = len(str(result.get("data", "")))
                notes = f"✅ Время: {execution_time:.1f}с, размер: {response_size} байт"
                success = True
                
                # Записываем в память
                self.memory_records.append({
                    "tool": tool_name,
                    "working_action": result.get("action", "default"),
                    "correct_params": result.get("params", {}),
                    "notes": notes,
                    "success": True
                })
            else:
                notes = f"❌ Ошибка: {result.get('error', 'Неизвестная ошибка')}"
                success = False
                
                # Проверяем на отсутствие ключей
                error_msg = result.get('error', '').lower()
                if any(word in error_msg for word in ['api', 'key', 'token', 'auth', 'install']):
                    key_req = self._extract_key_requirement(result.get('error', ''))
                    if key_req:
                        self.missing_keys.append({
                            "tool": tool_name,
                            "error": result.get('error', ''),
                            "likely_missing_key": key_req
                        })
                
        except Exception as e:
            execution_time = time.time() - start_time
            notes = f"❌ Исключение: {str(e)[:100]}"
            success = False
            
        self.results.append({
            "tool": tool_name,
            "success": success,
            "notes": notes,
            "execution_time": execution_time
        })
        
        print(f"   {notes}")
    
    def _extract_key_requirement(self, error_msg: str) -> str:
        """Извлечение требования API ключа"""
        error_lower = error_msg.lower()
        
        key_patterns = {
            "openrouter": "OPENROUTER_API_KEY",
            "replicate": "REPLICATE_API_TOKEN", 
            "telegram": "TELEGRAM_BOT_TOKEN + pip install pyrogram",
            "email": "EMAIL_PASSWORD или SMTP настройки",
            "database": "DATABASE_URL или настройки БД",
            "pyrogram": "pip install pyrogram",
            "sqlalchemy": "pip install sqlalchemy",
            "redis": "pip install redis",
            "pymongo": "pip install pymongo"
        }
        
        for pattern, key_name in key_patterns.items():
            if pattern in error_lower:
                return key_name
                
        return None
    
    async def _test_api_request(self):
        """Тест ApiRequestTool"""
        from kittycore.tools import ApiRequestTool
        
        tool = ApiRequestTool()
        result = tool.execute(url="https://httpbin.org/get", method="GET")
        
        return {
            "success": result.success,
            "error": getattr(result, 'error', None),
            "data": getattr(result, 'data', {}),
            "action": "request",
            "params": {"url": "string", "method": "GET|POST|PUT|DELETE"}
        }
    
    async def _test_super_system(self):
        """Тест SuperSystemTool"""
        from kittycore.tools import SuperSystemTool
        
        tool = SuperSystemTool()
        result = tool.execute(action="get_system_info")
        
        return {
            "success": result.success,
            "error": getattr(result, 'error', None),
            "data": getattr(result, 'data', {}),
            "action": "get_system_info",
            "params": {"action": "get_system_info|get_processes|get_resource_usage"}
        }
    
    async def _test_email(self):
        """Тест EmailTool"""
        from kittycore.tools import EmailTool
        
        tool = EmailTool()
        result = tool.execute(
            to="test@example.com",
            subject="Тест KittyCore", 
            body="Тестовое письмо"
        )
        
        return {
            "success": result.success,
            "error": getattr(result, 'error', None),
            "data": getattr(result, 'data', {}),
            "action": "send_email",
            "params": {"to": "string", "subject": "string", "body": "string"}
        }
    
    async def _test_computer_use(self):
        """Тест ComputerUseTool - правильный API"""
        from kittycore.tools import ComputerUseTool
        
        tool = ComputerUseTool()
        # ComputerUseTool.execute принимает Dict с params
        result = await tool.execute({"action": "screenshot"})
        
        return {
            "success": result.get("success", False),
            "error": result.get("error"),
            "data": result,
            "action": "screenshot",
            "params": {"action": "screenshot|click|type_text|key_press"}
        }
    
    async def _test_database(self):
        """Тест DatabaseTool - async execute"""
        from kittycore.tools import DatabaseTool
        
        tool = DatabaseTool()
        # DatabaseTool.execute - это async функция
        result = await tool.execute("SELECT 1 as test")
        
        return {
            "success": result.success,
            "error": getattr(result, 'error', None),
            "data": getattr(result, 'data', {}),
            "action": "execute_query",
            "params": {"query": "SQL string"}
        }
    
    async def _test_ai_integration(self):
        """Тест AIIntegrationTool - async execute"""
        from kittycore.tools import AIIntegrationTool
        
        tool = AIIntegrationTool()
        # AIIntegrationTool.execute - это async функция
        result = await tool.execute(action="list_models")
        
        return {
            "success": result.success,
            "error": getattr(result, 'error', None),
            "data": getattr(result, 'data', {}),
            "action": "list_models",
            "params": {"action": "list_models|list_providers|get_info"}
        }
    
    async def _test_security(self):
        """Тест SecurityTool - async execute"""
        from kittycore.tools import SecurityTool
        
        tool = SecurityTool()
        # SecurityTool.execute - это async функция
        result = await tool.execute(action="system_scan")
        
        return {
            "success": result.success,
            "error": getattr(result, 'error', None),
            "data": getattr(result, 'data', {}),
            "action": "system_scan",
            "params": {"action": "system_scan|check_ports|analyze_file"}
        }
    
    async def _test_smart_function(self):
        """Тест SmartFunctionTool - async execute"""
        from kittycore.tools import SmartFunctionTool
        
        tool = SmartFunctionTool()
        # SmartFunctionTool.execute - это async функция
        result = await tool.execute(action="get_info")
        
        return {
            "success": result.success,
            "error": getattr(result, 'error', None),
            "data": getattr(result, 'data', {}),
            "action": "get_info",
            "params": {"action": "get_info|execute_function|list_functions"}
        }
    
    async def _test_vector_search(self):
        """Тест VectorSearchTool"""
        from kittycore.tools import VectorSearchTool
        
        tool = VectorSearchTool()
        # VectorSearchTool.execute принимает query
        result = tool.execute("test query")
        
        return {
            "success": result.success,
            "error": getattr(result, 'error', None),
            "data": getattr(result, 'data', {}),
            "action": "search",
            "params": {"query": "string", "limit": "int"}
        }
    
    async def _test_image_generation(self):
        """Тест ImageGenerationTool - async execute"""
        from kittycore.tools import ImageGenerationTool
        
        tool = ImageGenerationTool()
        # ImageGenerationTool.execute - это async функция
        result = await tool.execute(action="get_info")
        
        return {
            "success": result.success,
            "error": getattr(result, 'error', None),
            "data": getattr(result, 'data', {}),
            "action": "get_info",
            "params": {"action": "get_info|generate_image|list_models"}
        }
    
    async def _test_document(self):
        """Тест DocumentTool"""
        from kittycore.tools import DocumentTool
        
        tool = DocumentTool()
        # DocumentTool.execute принимает command
        result = tool.execute(command="get_info")
        
        return {
            "success": result.success,
            "error": getattr(result, 'error', None),
            "data": getattr(result, 'data', {}),
            "action": "get_info",
            "params": {"command": "get_info|process_file|extract_text"}
        }
    
    async def _test_web_scraping(self):
        """Тест EnhancedWebScrapingTool - async execute"""
        from kittycore.tools import EnhancedWebScrapingTool
        
        tool = EnhancedWebScrapingTool()
        # EnhancedWebScrapingTool.execute - это async функция
        result = await tool.execute(url="https://httpbin.org/json", extract_text=True)
        
        return {
            "success": result.success,
            "error": getattr(result, 'error', None),
            "data": getattr(result, 'data', {}),
            "action": "scrape",
            "params": {"url": "string", "extract_text": "bool"}
        }
    
    async def _test_web_client(self):
        """Тест WebClient"""
        from kittycore.tools import WebClient
        
        tool = WebClient()
        # WebClient.execute принимает url и method
        result = tool.execute(url="https://httpbin.org/user-agent", method="GET")
        
        return {
            "success": result.success,
            "error": getattr(result, 'error', None),
            "data": getattr(result, 'data', {}),
            "action": "request",
            "params": {"url": "string", "method": "GET|POST"}
        }
    
    async def _test_telegram(self):
        """Тест TelegramTool"""
        from kittycore.tools import TelegramTool
        
        try:
            tool = TelegramTool()
            result = tool.execute(
                chat_id="@test_channel",
                message="Тест KittyCore"
            )
            
            return {
                "success": result.success,
                "error": getattr(result, 'error', None),
                "data": getattr(result, 'data', {}),
                "action": "send_message",
                "params": {"chat_id": "string", "message": "string"}
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "data": {},
                "action": "send_message",
                "params": {"chat_id": "string", "message": "string"}
            }
    
    def _print_results(self):
        """Вывод результатов"""
        
        print("\n" + "=" * 80)
        print("📊 РЕЗУЛЬТАТЫ ФИНАЛЬНОГО COMPREHENSIVE ТЕСТИРОВАНИЯ")
        print("=" * 80)
        
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
            print(f"\n🔑 ОТСУТСТВУЮЩИЕ API КЛЮЧИ/ЗАВИСИМОСТИ ({len(self.missing_keys)}):")
            for missing in self.missing_keys:
                print(f"   🔧 {missing['tool']}: {missing['likely_missing_key']}")
    
    def _save_results(self):
        """Сохранение результатов"""
        
        Path("test_final_comprehensive").mkdir(exist_ok=True)
        
        # Детальные результаты
        with open("test_final_comprehensive/results.json", 'w', encoding='utf-8') as f:
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
        with open("test_final_comprehensive/memory_records.json", 'w', encoding='utf-8') as f:
            json.dump(self.memory_records, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 Результаты сохранены в test_final_comprehensive/")

async def main():
    """Главная функция"""
    tester = FinalComprehensiveTester()
    await tester.test_all_tools()

if __name__ == "__main__":
    asyncio.run(main()) 