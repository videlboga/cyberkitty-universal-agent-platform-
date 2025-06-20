#!/usr/bin/env python3
"""
💾 СОХРАНЕНИЕ ВСЕХ УСПЕШНЫХ РЕЗУЛЬТАТОВ ТЕСТИРОВАНИЯ В ПАМЯТЬ KITTYCORE 3.0
Объединяем все успешные инструменты из разных тестов
"""

import json
import sys
import asyncio
from pathlib import Path

# Добавляем путь к KittyCore
sys.path.append(str(Path(__file__).parent / 'kittycore'))

from kittycore.memory.enhanced_memory import EnhancedCollectiveMemory

class AllSuccessfulToolsSaver:
    def __init__(self):
        self.memory = EnhancedCollectiveMemory(team_id="comprehensive_tool_testing")
        
    async def save_all_successful_tools(self):
        """Сохранение всех успешных инструментов в память"""
        
        print("💾 СОХРАНЕНИЕ ВСЕХ УСПЕШНЫХ РЕЗУЛЬТАТОВ В ПАМЯТЬ KITTYCORE 3.0")
        print("=" * 80)
        
        # Собираем все успешные результаты из разных тестов
        all_successful = []
        
        # 1. Из первого успешного теста (enhanced_web_search, media_tool, network_tool)
        if Path("test_real_tools_final/memory_records.json").exists():
            with open("test_real_tools_final/memory_records.json", 'r', encoding='utf-8') as f:
                first_batch = json.load(f)
                all_successful.extend(first_batch)
                print(f"📄 Загружено {len(first_batch)} записей из test_real_tools_final")
        
        # 2. Из исправленного теста (api_request_tool, super_system_tool, email_tool)
        if Path("test_tools_fixed_api/memory_records.json").exists():
            with open("test_tools_fixed_api/memory_records.json", 'r', encoding='utf-8') as f:
                second_batch = json.load(f)
                all_successful.extend(second_batch)
                print(f"📄 Загружено {len(second_batch)} записей из test_tools_fixed_api")
        
        # 3. Из финального теста (computer_use_tool)
        if Path("test_final_comprehensive/memory_records.json").exists():
            with open("test_final_comprehensive/memory_records.json", 'r', encoding='utf-8') as f:
                third_batch = json.load(f)
                all_successful.extend(third_batch)
                print(f"📄 Загружено {len(third_batch)} записей из test_final_comprehensive")
        
        # Удаляем дубликаты по названию инструмента
        unique_tools = {}
        for record in all_successful:
            tool_name = record['tool']
            if tool_name not in unique_tools:
                unique_tools[tool_name] = record
        
        print(f"🔧 Уникальных инструментов: {len(unique_tools)}")
        print()
        
        # Сохраняем каждый успешный инструмент в память
        saved_count = 0
        
        for tool_name, record in unique_tools.items():
            try:
                # Подготавливаем данные для памяти
                memory_content = {
                    "tool_name": tool_name,
                    "working_action": record.get("working_action", "default"),
                    "correct_params": record.get("correct_params", {}),
                    "performance": record.get("notes", ""),
                    "tested_successfully": True,
                    "test_type": "comprehensive_real_testing"
                }
                
                # Записываем в память A-MEM
                memory_id = await self.memory.store(
                    content=json.dumps(memory_content, ensure_ascii=False, indent=2),
                    tags=[
                        "tool_usage", 
                        "verified", 
                        "successful", 
                        tool_name, 
                        record.get("working_action", "default"),
                        "comprehensive_testing",
                        "no_mocks"
                    ]
                )
                
                saved_count += 1
                print(f"   ✅ {tool_name}.{record.get('working_action', 'default')} → сохранено (ID: {memory_id})")
                
            except Exception as e:
                print(f"   ❌ Ошибка сохранения {tool_name}: {e}")
        
        print()
        print(f"🎯 ИТОГОВАЯ СТАТИСТИКА:")
        print(f"   📊 Всего уникальных инструментов: {len(unique_tools)}")
        print(f"   💾 Успешно сохранено в память: {saved_count}")
        print(f"   📈 Процент сохранения: {(saved_count/len(unique_tools)*100):.1f}%")
        
        # Создаём итоговый отчёт
        await self._create_final_report(unique_tools)
    
    async def _create_final_report(self, unique_tools):
        """Создание итогового отчёта по тестированию"""
        
        print(f"\n📋 СОЗДАНИЕ ИТОГОВОГО ОТЧЁТА...")
        
        # Категоризация инструментов
        categories = {
            "Веб-инструменты": ["enhanced_web_search_tool", "api_request_tool", "enhanced_web_scraping_tool", "web_client_tool"],
            "Системные инструменты": ["super_system_tool", "computer_use_tool", "security_tool"],
            "Коммуникация": ["email_tool", "telegram_tool"],
            "Данные и AI": ["database_tool", "ai_integration_tool", "smart_function_tool", "vector_search_tool"],
            "Медиа и контент": ["media_tool", "image_generation_tool", "document_tool"],
            "Сетевые операции": ["network_tool"]
        }
        
        report = {
            "summary": {
                "total_tested_tools": len(unique_tools),
                "testing_approach": "Real API calls without mocks",
                "test_date": "2025-06-18",
                "system": "KittyCore 3.0 - Саморедуплицирующаяся агентная система"
            },
            "successful_tools": {},
            "categories_analysis": {}
        }
        
        # Анализ по категориям
        for category, tool_list in categories.items():
            successful_in_category = [tool for tool in tool_list if tool in unique_tools]
            total_in_category = len(tool_list)
            success_rate = (len(successful_in_category) / total_in_category * 100) if total_in_category > 0 else 0
            
            report["categories_analysis"][category] = {
                "successful": len(successful_in_category),
                "total": total_in_category,
                "success_rate": success_rate,
                "working_tools": successful_in_category
            }
        
        # Детали успешных инструментов
        for tool_name, record in unique_tools.items():
            report["successful_tools"][tool_name] = {
                "working_action": record.get("working_action", "default"),
                "correct_params": record.get("correct_params", {}),
                "performance_notes": record.get("notes", ""),
                "status": "verified_working"
            }
        
        # Сохраняем отчёт
        with open("COMPREHENSIVE_TOOLS_TESTING_REPORT.json", 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"   📄 Итоговый отчёт: COMPREHENSIVE_TOOLS_TESTING_REPORT.json")
        
        # Выводим краткую статистику
        print(f"\n📊 КРАТКАЯ СТАТИСТИКА ПО КАТЕГОРИЯМ:")
        for category, analysis in report["categories_analysis"].items():
            print(f"   🔧 {category}: {analysis['successful']}/{analysis['total']} = {analysis['success_rate']:.1f}%")

async def main():
    """Главная функция"""
    saver = AllSuccessfulToolsSaver()
    await saver.save_all_successful_tools()

if __name__ == "__main__":
    asyncio.run(main()) 