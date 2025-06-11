#!/usr/bin/env python3

import asyncio
import kittycore

async def simple_test():
    print("🐱 KittyCore 3.0 - Простой тест реальных инструментов")
    print("=" * 55)
    
    orchestrator = kittycore.create_orchestrator()
    
    task = "создать веб-страницу с контактами CyberKitty"
    
    result = await orchestrator.solve_task(task)
    
    print(f"✅ Задача: {task}")
    print(f"📊 Статус: {result['status']}")
    print(f"⏱️ Время: {result['duration']:.2f}с")
    
    if result['status'] == 'completed':
        execution = result.get('execution', {})
        files = execution.get('files_created', [])
        
        print(f"\n📁 Созданные файлы ({len(files)}):")
        for file in files:
            print(f"   📄 {file}")
        
        step_results = execution.get('step_results', {})
        print(f"\n🔧 Действия агентов:")
        for step_id, step_result in step_results.items():
            status = "✅" if step_result.get('status') == 'completed' else "❌"
            output = step_result.get('result', 'No output')
            print(f"   {status} {output}")

if __name__ == "__main__":
    asyncio.run(simple_test()) 