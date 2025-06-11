#!/usr/bin/env python3
import asyncio
import kittycore

async def quick_test():
    print("🔍 Быстрый тест KittyCore 3.0")
    
    orchestrator = kittycore.create_orchestrator()
    task = "создать python файл с приветствием"
    
    print(f"📝 Задача: {task}")
    result = await orchestrator.solve_task(task)
    
    print(f"📊 Статус: {result.get('status', 'unknown')}")
    print(f"⏱️ Время: {result.get('duration', 0):.2f}с")
    
    # Проверяем execution
    execution = result.get('execution', {})
    print(f"🔧 Execution: {execution}")
    
    files = execution.get('files_created', [])
    print(f"📁 Файлы: {files}")

if __name__ == "__main__":
    asyncio.run(quick_test()) 