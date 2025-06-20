#!/usr/bin/env python3
"""
🧪 COMPREHENSIVE РЕАЛЬНОЕ ТЕСТИРОВАНИЕ ВСЕХ ИНСТРУМЕНТОВ KITTYCORE 3.0
Без моков! Только реальные API вызовы и валидация результатов.

ЦЕЛЬ: протестировать все 18 инструментов, выявить проблемы API ключей, 
записать успешные результаты в память для будущего использования.
"""

import sys
import asyncio
import json
import time
from pathlib import Path
from typing import Dict, List, Any

# Добавляем путь к KittyCore
sys.path.append(str(Path(__file__).parent / 'kittycore'))

from kittycore.tools import (
    # Уже протестированные (пропускаем)
    # EnhancedWebSearchTool, MediaTool, NetworkTool, CodeExecutionTool, DataAnalysisTool,
    
    # НОВЫЕ для тестирования
    EnhancedWebScrapingTool,  # 1. Веб-скрапинг
    ApiRequestTool,           # 2. API запросы  
    WebClient,                # 3. Веб-клиент
    SuperSystemTool,          # 4. Системный инструмент
    DocumentTool,             # 5. Документооборот
    ComputerUseTool,          # 6. GUI автоматизация
    AIIntegrationTool,        # 7. AI интеграция
    SecurityTool,             # 8. Безопасность
    ImageGenerationTool,      # 9. Генерация изображений
    SmartFunctionTool,        # 10. Умные функции
    DatabaseTool,             # 11. Базы данных
    VectorSearchTool,         # 12. Семантический поиск
    EmailTool,                # 13. Email
    TelegramTool              # 14. Telegram
)

class ComprehensiveToolsTester:
    def __init__(self):
        self.results = []
        self.memory_records = []
        self.total_tests = 0
        self.successful_tests = 0
        self.missing_keys = []
        
    async def test_tool_async(self, tool, tool_name: str, test_config: dict) -> dict:
        """Тестирование асинхронного инструмента"""
        start_time = time.time()
        
        try:
            result = await tool.execute(**test_config.get("params", {}))
            execution_time = time.time() - start_time
            
            # Валидация результата
            if hasattr(result, 'success') and result.success:
                response_data = getattr(result, 'data', {})
                response_size = len(str(response_data))
                
                if response_size > 50:  # Минимальный размер для реального ответа
                    success = True
                    notes = f"✅ Время: {execution_time:.1f}с, размер: {response_size} байт"
                else:
                    success = False
                    notes = f"❌ Подозрительно маленький ответ: {response_size} байт"
            else:
                success = False
                error_msg = getattr(result, 'error', 'Неизвестная ошибка')
                notes = f"❌ Ошибка: {error_msg}"
                
        except Exception as e:
            execution_time = time.time() - start_time
            success = False
            notes = f"❌ Исключение: {str(e)[:100]}"
            
            # Проверяем на отсутствие API ключей
            error_str = str(e).lower()
            if any(key_hint in error_str for key_hint in ['api', 'key', 'token', 'auth']):
                if tool_name not in [record["tool"] for record in self.missing_keys]:
                    self.missing_keys.append({
                        "tool": tool_name,
                        "error": str(e),
                        "likely_missing_key": self._extract_key_requirement(str(e))
                    })
        
        return {
            "tool": tool_name,
            "success": success,
            "execution_time": execution_time,
            "notes": notes,
            "test_config": test_config
        }
    
    def test_tool_sync(self, tool, tool_name: str, test_config: dict) -> dict:
        """Тестирование синхронного инструмента"""
        start_time = time.time()
        
        try:
            result = tool.execute(**test_config.get("params", {}))
            execution_time = time.time() - start_time
            
            # Валидация результата
            if hasattr(result, 'success') and result.success:
                response_data = getattr(result, 'data', {})
                response_size = len(str(response_data))
                
                if response_size > 50:  # Минимальный размер для реального ответа
                    success = True
                    notes = f"✅ Время: {execution_time:.1f}с, размер: {response_size} байт"
                else:
                    success = False
                    notes = f"❌ Подозрительно маленький ответ: {response_size} байт"
            else:
                success = False
                error_msg = getattr(result, 'error', 'Неизвестная ошибка')
                notes = f"❌ Ошибка: {error_msg}"
                
        except Exception as e:
            execution_time = time.time() - start_time
            success = False
            notes = f"❌ Исключение: {str(e)[:100]}"
            
            # Проверяем на отсутствие API ключей
            error_str = str(e).lower()
            if any(key_hint in error_str for key_hint in ['api', 'key', 'token', 'auth']):
                if tool_name not in [record["tool"] for record in self.missing_keys]:
                    self.missing_keys.append({
                        "tool": tool_name,
                        "error": str(e),
                        "likely_missing_key": self._extract_key_requirement(str(e))
                    })
        
        return {
            "tool": tool_name,
            "success": success,
            "execution_time": execution_time,
            "notes": notes,
            "test_config": test_config
        }
    
    def _extract_key_requirement(self, error_msg: str) -> str:
        """Извлекает название требуемого API ключа из ошибки"""
        error_lower = error_msg.lower()
        
        key_patterns = {
            "openrouter": "OPENROUTER_API_KEY",
            "replicate": "REPLICATE_API_TOKEN", 
            "telegram": "TELEGRAM_BOT_TOKEN",
            "email": "EMAIL_PASSWORD или SMTP настройки",
            "database": "DATABASE_URL или DB_CONNECTION",
            "openai": "OPENAI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY"
        }
        
        for pattern, key_name in key_patterns.items():
            if pattern in error_lower:
                return key_name
                
        return "Неизвестный API ключ (см. ошибку)"
    
    async def run_comprehensive_test(self):
        """Запуск comprehensive тестирования всех инструментов"""
        
        print("🧪 COMPREHENSIVE РЕАЛЬНОЕ ТЕСТИРОВАНИЕ ВСЕХ ИНСТРУМЕНТОВ KITTYCORE 3.0")
        print("=" * 80)
        print("🚫 БЕЗ МОКОВ! Только реальные API вызовы")
        print("🔍 Цель: выявить проблемы, записать успешные результаты в память")
        print()
        
        # === ТЕСТОВЫЕ КОНФИГУРАЦИИ ===
        test_configs = {
            # 1. ВЕБ-ИНСТРУМЕНТЫ
            "enhanced_web_scraping": {
                "tool_class": EnhancedWebScrapingTool,
                "is_async": True,
                "params": {"url": "https://httpbin.org/json", "extract_text": True}
            },
            "api_request": {
                "tool_class": ApiRequestTool,
                "is_async": False,
                "params": {"url": "https://httpbin.org/get", "method": "GET"}
            },
            "web_client": {
                "tool_class": WebClient,
                "is_async": False,
                "params": {"action": "get", "url": "https://httpbin.org/user-agent"}
            },
            
            # 2. СИСТЕМНЫЕ ИНСТРУМЕНТЫ
            "super_system": {
                "tool_class": SuperSystemTool,
                "is_async": False,
                "params": {"action": "list_processes", "limit": 5}
            },
            "document": {
                "tool_class": DocumentTool,
                "is_async": False,
                "params": {"action": "get_info"}
            },
            "computer_use": {
                "tool_class": ComputerUseTool,
                "is_async": False,
                "params": {"action": "screenshot"}
            },
            
            # 3. AI И БЕЗОПАСНОСТЬ
            "ai_integration": {
                "tool_class": AIIntegrationTool,
                "is_async": True,
                "params": {"action": "list_models"}
            },
            "security": {
                "tool_class": SecurityTool,
                "is_async": False,
                "params": {"action": "system_scan"}
            },
            
            # 4. КРЕАТИВНЫЕ ИНСТРУМЕНТЫ
            "image_generation": {
                "tool_class": ImageGenerationTool,
                "is_async": True,
                "params": {"action": "get_info"}
            },
            "smart_function": {
                "tool_class": SmartFunctionTool,
                "is_async": False,
                "params": {"action": "get_info"}
            },
            
            # 5. ДАННЫЕ И ПОИСК
            "database": {
                "tool_class": DatabaseTool,
                "is_async": False,
                "params": {"action": "get_info"}
            },
            "vector_search": {
                "tool_class": VectorSearchTool,
                "is_async": False,
                "params": {"action": "get_info"}
            },
            
            # 6. КОММУНИКАЦИЯ
            "email": {
                "tool_class": EmailTool,
                "is_async": False,
                "params": {"action": "get_info"}
            },
            "telegram": {
                "tool_class": TelegramTool,
                "is_async": False,
                "params": {"action": "get_info"}
            }
        }
        
        # === ВЫПОЛНЕНИЕ ТЕСТОВ ===
        for tool_name, config in test_configs.items():
            print(f"🔧 Тестирую {tool_name}...")
            
            try:
                # Инициализация инструмента
                tool = config["tool_class"]()
                self.total_tests += 1
                
                # Выполнение теста
                if config["is_async"]:
                    result = await self.test_tool_async(tool, tool_name, config)
                else:
                    result = self.test_tool_sync(tool, tool_name, config)
                
                self.results.append(result)
                
                if result["success"]:
                    self.successful_tests += 1
                    print(f"   ✅ {result['notes']}")
                    
                    # Записываем успешный результат для памяти
                    self.memory_records.append({
                        "tool": tool_name,
                        "working_action": config["params"].get("action", "default"),
                        "correct_params": config["params"],
                        "notes": result["notes"],
                        "success": True,
                        "response_size": len(result["notes"])
                    })
                else:
                    print(f"   ❌ {result['notes']}")
                    
            except Exception as e:
                print(f"   💥 Критическая ошибка инициализации: {str(e)[:100]}")
                self.results.append({
                    "tool": tool_name,
                    "success": False,
                    "execution_time": 0,
                    "notes": f"💥 Ошибка инициализации: {str(e)[:100]}",
                    "test_config": config
                })
        
        # === РЕЗУЛЬТАТЫ ===
        self._print_results()
        self._save_results()
    
    def _print_results(self):
        """Вывод результатов тестирования"""
        
        print("\n" + "=" * 80)
        print("📊 РЕЗУЛЬТАТЫ COMPREHENSIVE ТЕСТИРОВАНИЯ")
        print("=" * 80)
        
        success_rate = (self.successful_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        print(f"🎯 Общий успех: {self.successful_tests}/{self.total_tests} = {success_rate:.1f}%")
        
        # Успешные инструменты
        successful = [r for r in self.results if r["success"]]
        if successful:
            print(f"\n✅ РАБОТАЮЩИЕ ИНСТРУМЕНТЫ ({len(successful)}):")
            for result in successful:
                print(f"   🔧 {result['tool']}: {result['notes']}")
        
        # Проблемные инструменты
        failed = [r for r in self.results if not r["success"]]
        if failed:
            print(f"\n❌ ПРОБЛЕМНЫЕ ИНСТРУМЕНТЫ ({len(failed)}):")
            for result in failed:
                print(f"   🔧 {result['tool']}: {result['notes']}")
        
        # Отсутствующие API ключи
        if self.missing_keys:
            print(f"\n🔑 ОТСУТСТВУЮЩИЕ API КЛЮЧИ ({len(self.missing_keys)}):")
            for missing in self.missing_keys:
                print(f"   🔧 {missing['tool']}: {missing['likely_missing_key']}")
                print(f"      Ошибка: {missing['error'][:100]}...")
    
    def _save_results(self):
        """Сохранение результатов"""
        
        # Сохраняем детальные результаты
        results_file = "test_all_tools_comprehensive/detailed_results.json"
        Path("test_all_tools_comprehensive").mkdir(exist_ok=True)
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump({
                "summary": {
                    "total_tests": self.total_tests,
                    "successful_tests": self.successful_tests,
                    "success_rate": (self.successful_tests / self.total_tests * 100) if self.total_tests > 0 else 0
                },
                "results": self.results,
                "missing_keys": self.missing_keys
            }, f, ensure_ascii=False, indent=2)
        
        # Сохраняем записи для памяти
        memory_file = "test_all_tools_comprehensive/memory_records.json"
        with open(memory_file, 'w', encoding='utf-8') as f:
            json.dump(self.memory_records, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 Результаты сохранены:")
        print(f"   📄 Детали: {results_file}")
        print(f"   🧠 Память: {memory_file}")

async def main():
    """Главная функция"""
    tester = ComprehensiveToolsTester()
    await tester.run_comprehensive_test()

if __name__ == "__main__":
    asyncio.run(main()) 