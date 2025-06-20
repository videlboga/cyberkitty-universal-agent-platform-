#!/usr/bin/env python3
"""
💾 СОХРАНЕНИЕ УСПЕШНЫХ ПРИМЕНЕНИЙ ИНСТРУМЕНТОВ В ПАМЯТЬ KITTYCORE 3.0
Записываем правильные параметры и примеры использования в основную память системы
"""

import json
import sys
import asyncio
from pathlib import Path

# Добавляем путь к KittyCore
sys.path.append(str(Path(__file__).parent / 'kittycore'))

from kittycore.memory.enhanced_memory import EnhancedCollectiveMemory

class ToolsMemorySaver:
    def __init__(self):
        self.memory = EnhancedCollectiveMemory(team_id="tool_testing_team")
        
    async def save_successful_tools_to_memory(self, memory_file: str):
        """Сохраняем успешные результаты тестирования в основную память KittyCore"""
        
        # Загружаем результаты тестирования
        with open(memory_file, 'r', encoding='utf-8') as f:
            memory_records = json.load(f)
        
        print(f"🧠 Сохраняю успешные применения инструментов в память KittyCore...")
        
        # Записываем только успешные применения
        successful_count = 0
        for record in memory_records:
            if record.get("success", False):
                tool_name = record["tool"]
                action = record["working_action"]
                params = record["correct_params"]
                notes = record["notes"]
                
                # Формируем детальную запись для памяти
                memory_content = {
                    "tool": tool_name,
                    "working_action": action,
                    "correct_parameters": params,
                    "performance_notes": notes,
                    "test_results": {
                        "success": True,
                        "verified": True,
                        "response_size": record.get("response_size", 0)
                    },
                    "usage_example": self._generate_usage_example(tool_name, action, params),
                    "type": "verified_tool_usage"
                }
                
                # Записываем в память с тегами
                memory_entry_id = await self.memory.store(
                    content=json.dumps(memory_content, ensure_ascii=False, indent=2),
                    agent_id="tool_tester",
                    tags=[
                        "tool_usage", 
                        "verified", 
                        "successful", 
                        tool_name, 
                        action,
                        "real_testing"
                    ]
                )
                
                successful_count += 1
                print(f"   ✅ {tool_name}.{action} → сохранено в память (ID: {memory_entry_id})")
        
        print(f"\n🎯 Сохранено {successful_count} успешных применений инструментов!")
        return successful_count
    
    def _generate_usage_example(self, tool_name: str, action: str, params: dict) -> str:
        """Генерирует пример использования инструмента"""
        
        if tool_name == "enhanced_web_search":
            return f"""
# Пример использования {tool_name}
tool = EnhancedWebSearchTool()
result = await tool.execute(
    query="ваш поисковый запрос",
    limit=5
)
if result.success:
    results = result.data["results"]
    print(f"Найдено {{len(results)}} результатов")
"""
        
        elif tool_name == "media_tool":
            return f"""
# Пример использования {tool_name}
tool = MediaTool()
result = tool.execute(action="get_info")
if result.success:
    print("Информация об инструменте:", result.data)
"""
        
        elif tool_name == "network_tool":
            return f"""
# Пример использования {tool_name}
tool = NetworkTool()
result = await tool.execute(
    action="ping_host",
    host="google.com",
    count=3
)
if result.success:
    print("Ping результат:", result.data)
"""
        
        else:
            param_str = ", ".join([f"{k}='{v}'" for k, v in params.items()])
            return f"""
# Пример использования {tool_name}
tool = {tool_name.title().replace('_', '')}()
result = tool.execute({param_str})
if result.success:
    print("Результат:", result.data)
"""
    
    async def search_tool_memories(self, tool_name: str = None):
        """Поиск записей об инструментах в памяти"""
        
        if tool_name:
            query = f"tool usage {tool_name}"
        else:
            query = "verified tool usage successful"
        
        memories = await self.memory.search(query, limit=10)
        
        print(f"🔍 Найдено {len(memories)} записей об инструментах в памяти:")
        
        for memory in memories:
            content = memory.content
            tags = ", ".join(memory.tags) if memory.tags else "нет тегов"
            print(f"   📝 ID: {memory.id}")
            print(f"      📋 Теги: {tags}")
            print(f"      📄 Контент: {content[:100]}...")
            print()
        
        return memories

async def main():
    """Главная функция"""
    print("🚀 СОХРАНЕНИЕ УСПЕШНЫХ ПРИМЕНЕНИЙ ИНСТРУМЕНТОВ В ПАМЯТЬ KITTYCORE 3.0")
    print("=" * 70)
    
    saver = ToolsMemorySaver()
    
    # Сохраняем результаты последнего теста
    memory_file = "test_real_tools_final/memory_records.json"
    
    if Path(memory_file).exists():
        await saver.save_successful_tools_to_memory(memory_file)
        
        print("\n" + "=" * 70)
        print("🔍 ПРОВЕРКА СОХРАНЁННЫХ ЗАПИСЕЙ:")
        
        # Ищем сохранённые записи
        await saver.search_tool_memories()
        
    else:
        print(f"❌ Файл {memory_file} не найден!")

if __name__ == "__main__":
    asyncio.run(main()) 