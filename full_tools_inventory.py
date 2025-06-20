#!/usr/bin/env python3
"""
📋 ПОЛНАЯ ИНВЕНТАРИЗАЦИЯ: Все инструменты KittyCore 3.0

ЦЕЛЬ: Определить какие инструменты протестированы, а какие нет
РЕЗУЛЬТАТ: Полный список с статусами тестирования
"""

import os
import importlib
import traceback

def discover_all_tools():
    """Обнаружить все инструменты в системе"""
    
    print("📋 ПОЛНАЯ ИНВЕНТАРИЗАЦИЯ ИНСТРУМЕНТОВ KITTYCORE 3.0")
    print("=" * 80)
    
    # Известные протестированные инструменты
    tested_tools = {
        # ✅ РАБОТАЮЩИЕ (ручно проверены)
        "EnhancedWebSearchTool": "✅ РАБОТАЕТ (поиск URLs)",
        "EnhancedWebScrapingTool": "✅ РАБОТАЕТ (скрапинг текста)",
        "SecurityTool": "✅ РАБОТАЕТ (анализ паролей)",
        "VectorSearchTool": "✅ РАБОТАЕТ (ChromaDB)",
        "ApiRequestTool": "✅ РАБОТАЕТ (HTTP запросы)",
        
        # ⚠️ ЧАСТИЧНО РАБОТАЮЩИЕ
        "DatabaseTool": "⚠️ ЧАСТИЧНО (async проблема)",
        "EmailTool": "⚠️ ЧАСТИЧНО (нужен SMTP)",
        "NetworkTool": "⚠️ ЧАСТИЧНО (нужна настройка)",
        
        # ✅ РАНЕЕ ПРОТЕСТИРОВАННЫЕ
        "SuperSystemTool": "✅ РАБОТАЕТ (системная информация)",
        "DocumentTool": "✅ РАБОТАЕТ (обработка документов)",
        "ComputerUseTool": "✅ ЧАСТИЧНО (без GUI)",
        "AIIntegrationTool": "❌ НЕ РАБОТАЕТ (нужен API ключ)",
        "DataAnalysisTool": "✅ РАБОТАЕТ (анализ CSV)",
        "MediaTool": "✅ РАБОТАЕТ (обработка медиа)",
        "CodeExecutionTool": "✅ ЧАСТИЧНО (50% успех)",
        "WebClientTool": "✅ РАБОТАЕТ (веб-клиент)",
        "SmartFunctionTool": "✅ РАБОТАЕТ (умные функции)",
        
        # ❌ НЕ РАБОТАЮЩИЕ (из ранних тестов)
        "TelegramTool": "❌ НЕ РАБОТАЕТ (нужен pyrogram)"
    }
    
    # Список файлов инструментов для проверки
    tool_files = [
        # Основные инструменты
        ("enhanced_web_search_tool.py", ["EnhancedWebSearchTool"]),
        ("enhanced_web_scraping_tool.py", ["EnhancedWebScrapingTool"]),
        ("security_tool.py", ["SecurityTool"]),
        ("vector_search_tool.py", ["VectorSearchTool"]),
        ("api_request_tool.py", ["ApiRequestTool"]),
        ("database_tool.py", ["DatabaseTool"]),
        ("network_tool.py", ["NetworkTool"]),
        ("super_system_tool.py", ["SuperSystemTool"]),
        ("ai_integration_tool.py", ["AIIntegrationTool"]),
        ("data_analysis_tool.py", ["DataAnalysisTool"]),
        ("media_tool.py", ["MediaTool"]),
        ("computer_use_tool.py", ["ComputerUseTool"]),
        ("smart_function_tool.py", ["SmartFunctionTool"]),
        ("web_client_tool.py", ["WebClientTool"]),
        ("code_execution_tools.py", ["CodeExecutionTool"]),
        ("communication_tools.py", ["EmailTool", "TelegramTool"]),
        
        # Возможно есть ещё инструменты
        ("document_tool_unified.py", ["DocumentTool"]),
        ("image_generation_tool.py", ["ImageGenerationTool"]),
        ("obsidian_tools.py", ["ObsidianTool"]),
        ("smart_code_generator.py", ["SmartCodeGenerator"]),
        ("web_tools.py", ["WebTool"]),
        ("real_tools.py", ["RealTool"]),
    ]
    
    discovered_tools = {}
    untested_tools = []
    
    print("🔍 ОБНАРУЖЕНИЕ ИНСТРУМЕНТОВ:")
    print("-" * 50)
    
    for filename, expected_tools in tool_files:
        file_path = f"kittycore.tools.{filename[:-3]}"  # убираем .py
        
        try:
            module = importlib.import_module(file_path)
            
            for tool_name in expected_tools:
                if hasattr(module, tool_name):
                    tool_class = getattr(module, tool_name)
                    
                    if tool_name in tested_tools:
                        status = tested_tools[tool_name]
                        discovered_tools[tool_name] = status
                        print(f"  📦 {tool_name}: {status}")
                    else:
                        discovered_tools[tool_name] = "❓ НЕ ПРОТЕСТИРОВАН"
                        untested_tools.append((tool_name, file_path, tool_class))
                        print(f"  📦 {tool_name}: ❓ НЕ ПРОТЕСТИРОВАН")
                else:
                    print(f"  ❌ {tool_name}: не найден в {filename}")
                    
        except Exception as e:
            print(f"  ❌ Ошибка импорта {filename}: {str(e)[:50]}...")
    
    # Статистика
    print("\n" + "=" * 80)
    print("📊 СТАТИСТИКА ИНСТРУМЕНТОВ")
    print("=" * 80)
    
    total = len(discovered_tools)
    working = len([s for s in discovered_tools.values() if "✅ РАБОТАЕТ" in s])
    partial = len([s for s in discovered_tools.values() if "⚠️ ЧАСТИЧНО" in s])
    broken = len([s for s in discovered_tools.values() if "❌ НЕ РАБОТАЕТ" in s])
    untested = len([s for s in discovered_tools.values() if "❓ НЕ ПРОТЕСТИРОВАН" in s])
    
    print(f"📦 ВСЕГО ОБНАРУЖЕНО: {total} инструментов")
    print(f"✅ ПОЛНОСТЬЮ РАБОТАЕТ: {working} ({working/total*100:.1f}%)")
    print(f"⚠️ ЧАСТИЧНО РАБОТАЕТ: {partial} ({partial/total*100:.1f}%)")
    print(f"❌ НЕ РАБОТАЕТ: {broken} ({broken/total*100:.1f}%)")
    print(f"❓ НЕ ПРОТЕСТИРОВАНО: {untested} ({untested/total*100:.1f}%)")
    
    tested_count = working + partial + broken
    print(f"\n🎯 ПРОТЕСТИРОВАНО: {tested_count}/{total} = {tested_count/total*100:.1f}%")
    
    # Список непротестированных
    if untested_tools:
        print("\n" + "=" * 80)
        print("❓ НЕПРОТЕСТИРОВАННЫЕ ИНСТРУМЕНТЫ (ТРЕБУЮТ ПРОВЕРКИ)")
        print("=" * 80)
        
        for i, (tool_name, file_path, tool_class) in enumerate(untested_tools, 1):
            print(f"{i:2d}. {tool_name}")
            print(f"    📁 Файл: {file_path}")
            
            # Попытка определить назначение по названию
            purpose = ""
            if "image" in tool_name.lower():
                purpose = "🎨 Генерация изображений"
            elif "obsidian" in tool_name.lower():
                purpose = "📝 Работа с Obsidian"
            elif "code" in tool_name.lower():
                purpose = "💻 Генерация кода"
            elif "web" in tool_name.lower():
                purpose = "🌐 Веб-инструменты"
            elif "real" in tool_name.lower():
                purpose = "🔧 Реальные инструменты"
            else:
                purpose = "❓ Назначение неясно"
            
            print(f"    🎯 Назначение: {purpose}")
            print()
    
    return discovered_tools, untested_tools

if __name__ == "__main__":
    discovered, untested = discover_all_tools()
    
    if untested:
        print("🚀 РЕКОМЕНДАЦИИ:")
        print("  1. Протестировать все непротестированные инструменты")
        print("  2. Исправить частично работающие инструменты")
        print("  3. Довести общую работоспособность до 90%+")
        print("=" * 80)
    else:
        print("🎉 ВСЕ ИНСТРУМЕНТЫ ПРОТЕСТИРОВАНЫ!") 