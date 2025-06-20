#!/usr/bin/env python3
"""
🔍 ПРОВЕРКА ЗАПИСЕЙ ИНСТРУМЕНТОВ В ПАМЯТИ KITTYCORE 3.0
"""

import sys
import asyncio
from pathlib import Path

# Добавляем путь к KittyCore
sys.path.append(str(Path(__file__).parent / 'kittycore'))

from kittycore.memory.enhanced_memory import EnhancedCollectiveMemory

async def check_tool_records():
    """Проверка записанных инструментов в памяти"""
    
    print("🔍 ПРОВЕРКА ЗАПИСЕЙ ИНСТРУМЕНТОВ В ПАМЯТИ KITTYCORE 3.0")
    print("=" * 60)
    
    # Инициализируем память
    memory = EnhancedCollectiveMemory(team_id="tool_testing_team")
    
    # Поиск записей об инструментах
    search_queries = [
        "tool usage",
        "verified successful",
        "enhanced_web_search",
        "media_tool",
        "network_tool"
    ]
    
    for query in search_queries:
        print(f"\n🔍 Поиск: '{query}'")
        
        try:
            results = await memory.search(query, limit=3)
            
            if results:
                print(f"   ✅ Найдено: {len(results)} записей")
                
                for i, result in enumerate(results):
                    content = result.content[:200] if hasattr(result, 'content') else str(result)[:200]
                    author = getattr(result, 'author_agent', 'unknown')
                    importance = getattr(result, 'importance', 'unknown')
                    
                    print(f"   📝 Запись {i+1}:")
                    print(f"      👤 Автор: {author}")
                    print(f"      ⭐ Важность: {importance}")
                    print(f"      📄 Контент: {content}...")
                    print()
            else:
                print("   ❌ Записей не найдено")
                
        except Exception as e:
            print(f"   ⚠️ Ошибка поиска: {e}")
    
    print("=" * 60)
    print("✅ Проверка завершена!")

if __name__ == "__main__":
    asyncio.run(check_tool_records()) 