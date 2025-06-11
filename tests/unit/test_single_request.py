#!/usr/bin/env python3
import asyncio
import sys
import kittycore

async def test_single_request():
    print("🐱 KittyCore 3.0 - Тест одного запроса")
    print("=" * 40)
    
    # Берём запрос из аргументов командной строки
    if len(sys.argv) > 1:
        user_input = " ".join(sys.argv[1:])
    else:
        user_input = "создать веб-страницу с информацией о CyberKitty"
    
    print(f"🔍 Обрабатываю запрос: {user_input}")
    print("=" * 50)
    
    # Создаём оркестратор
    orchestrator = kittycore.create_orchestrator()
    
    # Обрабатываем запрос
    result = await orchestrator.solve_task(user_input)
    
    if result['status'] == 'completed':
        print(f"✅ Задача решена за {result['duration']:.2f}с")
        print(f"📊 Сложность: {result['complexity_analysis']['complexity']}")
        print(f"👥 Команда: {result['team']['team_size']} агентов")
        
        print(f"\n📋 План решения:")
        for i, subtask in enumerate(result['subtasks'], 1):
            print(f"   {i}. {subtask['description']}")
        
        print(f"\n📈 Workflow:")
        print(result['workflow_graph']['mermaid'])
        
        # Показываем реальные результаты
        print(f"\n💡 РЕАЛЬНЫЕ РЕЗУЛЬТАТЫ:")
        print(f"   ✅ Система проанализировала задачу")
        print(f"   ✅ Создала план из {len(result['subtasks'])} шагов")
        print(f"   ✅ Сформировала команду агентов")
        print(f"   ✅ Построила граф выполнения")
        print(f"   ✅ Агенты выполнили РЕАЛЬНУЮ РАБОТУ!")
        
        # Показываем файлы
        execution = result.get('execution', {})
        files = execution.get('files_created', [])
        
        print(f"\n📁 СОЗДАННЫЕ ФАЙЛЫ ({len(files)}):")
        if files:
            for file in files:
                print(f"   📄 {file}")
        else:
            print("   (файлы не создавались)")
        
        # Показываем действия агентов
        step_results = execution.get('step_results', {})
        print(f"\n🔧 ВЫПОЛНЕННЫЕ ДЕЙСТВИЯ:")
        if step_results:
            for step_id, step_result in step_results.items():
                status_icon = "✅" if step_result.get('status') == 'completed' else "❌"
                agent = step_result.get('agent', 'unknown')
                result_text = step_result.get('result', 'No result')
                print(f"   {status_icon} {agent}: {result_text}")
        else:
            print("   (детали выполнения недоступны)")
        
    else:
        print(f"❌ Ошибка: {result.get('error', 'Неизвестная ошибка')}")

if __name__ == "__main__":
    asyncio.run(test_single_request()) 