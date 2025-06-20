#!/usr/bin/env python3
"""
🚀 ОТЛАДКА: super_system_tool
"""

import time
import json
import tempfile
import os

try:
    from kittycore.tools.super_system_tool import SuperSystemTool
    IMPORT_OK = True
    print("✅ Импорт super_system_tool успешен")
except ImportError as e:
    print(f"❌ ИМПОРТ ОШИБКА: {e}")
    IMPORT_OK = False

def test_system_info():
    """Тест получения системной информации"""
    if not IMPORT_OK:
        return "IMPORT_ERROR"
    
    print("\n🖥️ Тестирую системную информацию...")
    tool = SuperSystemTool()
    
    result = tool.execute(action="get_system_info")
    
    print(f"📊 Результат: {type(result)}")
    if hasattr(result, 'success'):
        print(f"✅ Success: {result.success}")
        if result.success and hasattr(result, 'data'):
            data = result.data
            print(f"📦 Размер: {len(str(data))} байт")
            
            # Проверяем основные поля системной информации
            if isinstance(data, dict):
                expected_fields = ['platform', 'hostname', 'cpu_count', 'memory_total_gb', 'architecture']
                found_fields = [field for field in expected_fields if field in data]
                print(f"🔑 Найдено полей: {len(found_fields)}/{len(expected_fields)}")
                print(f"   Поля: {found_fields}")
                
                # Проверяем конкретные значения
                if 'platform' in data:
                    print(f"   Platform: {data['platform']}")
                if 'cpu_count' in data:
                    print(f"   CPU count: {data['cpu_count']}")
    
    return result

def test_resource_usage():
    """Тест получения использования ресурсов"""
    if not IMPORT_OK:
        return "IMPORT_ERROR"
    
    print("\n📊 Тестирую использование ресурсов...")
    tool = SuperSystemTool()
    
    result = tool.execute(action="get_resource_usage")
    
    print(f"📊 Результат: {type(result)}")
    if hasattr(result, 'success') and result.success:
        data = result.data
        if isinstance(data, dict):
            # Проверяем ключевые метрики
            metrics = ['cpu_percent', 'memory_percent', 'disk_usage_percent']
            for metric in metrics:
                if metric in data:
                    value = data[metric]
                    print(f"   {metric}: {value}%")
    
    return result

def test_file_operations():
    """Тест безопасных файловых операций"""
    if not IMPORT_OK:
        return "IMPORT_ERROR"
    
    print("\n📁 Тестирую файловые операции...")
    tool = SuperSystemTool()
    
    # Создаем временный файл
    temp_content = "Test content from SuperSystemTool"
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        temp_path = f.name
        f.write(temp_content)
    
    try:
        # Тест чтения файла
        read_result = tool.execute(
            action="safe_file_read",
            path=temp_path
        )
        
        print(f"📖 Чтение файла: {read_result.success if hasattr(read_result, 'success') else 'ERROR'}")
        if hasattr(read_result, 'success') and read_result.success:
            data = read_result.data
            if isinstance(data, dict) and 'content' in data:
                content = data['content']
                print(f"   Содержимое: {repr(content[:50])}")
                if temp_content in content:
                    print("✅ Реальное содержимое найдено!")
        
        # Тест информации о файле
        info_result = tool.execute(
            action="file_info",
            path=temp_path
        )
        
        print(f"📋 Информация о файле: {info_result.success if hasattr(info_result, 'success') else 'ERROR'}")
        if hasattr(info_result, 'success') and info_result.success:
            data = info_result.data
            if isinstance(data, dict):
                size = data.get('size', 0)
                print(f"   Размер файла: {size} байт")
        
        return read_result
        
    finally:
        # Удаляем временный файл
        try:
            os.unlink(temp_path)
        except:
            pass

def test_processes():
    """Тест информации о процессах"""
    if not IMPORT_OK:
        return "IMPORT_ERROR"
    
    print("\n🔄 Тестирую информацию о процессах...")
    tool = SuperSystemTool()
    
    result = tool.execute(
        action="get_processes",
        limit=5
    )
    
    print(f"📊 Результат: {type(result)}")
    if hasattr(result, 'success') and result.success:
        data = result.data
        if isinstance(data, dict) and 'processes' in data:
            processes = data['processes']
            print(f"   Найдено процессов: {len(processes)}")
            
            # Показываем первый процесс
            if processes and len(processes) > 0:
                first_proc = processes[0]
                if isinstance(first_proc, dict):
                    print(f"   Первый процесс: PID={first_proc.get('pid', 'НЕТ')}, name={first_proc.get('name', 'НЕТ')}")
    
    return result

def is_result_honest(result, test_name):
    """Проверка честности результата"""
    if not result:
        print(f"❌ {test_name}: Пустой результат")
        return False
    
    if not hasattr(result, 'success'):
        print(f"❌ {test_name}: Нет атрибута success")
        return False
    
    if not result.success:
        print(f"❌ {test_name}: success=False")
        if hasattr(result, 'error'):
            print(f"   Ошибка: {result.error}")
        return False
    
    if not hasattr(result, 'data') or not result.data:
        print(f"❌ {test_name}: Нет данных")
        return False
    
    data = result.data
    data_str = str(data)
    data_size = len(data_str)
    
    # Проверка на фейковые паттерны
    fake_patterns = [
        "super_system: успешно",
        "демо система",
        "заглушка системы"
    ]
    
    for pattern in fake_patterns:
        if pattern.lower() in data_str.lower():
            print(f"❌ {test_name}: Найден фейковый паттерн: {pattern}")
            return False
    
    # Проверка на реальные системные данные
    system_indicators = [
        "linux", "windows", "cpu_count", "memory", "disk", "platform", 
        "hostname", "architecture", "process", "pid", "size", "content"
    ]
    
    has_system_data = any(indicator.lower() in data_str.lower() for indicator in system_indicators)
    
    if not has_system_data:
        print(f"❌ {test_name}: Нет признаков реальных системных данных")
        return False
    
    if data_size < 50:
        print(f"❌ {test_name}: Слишком маленький результат ({data_size} байт)")
        return False
    
    print(f"✅ {test_name}: ЧЕСТНЫЙ результат ({data_size} байт)")
    return True

def main():
    print("🚀 ОТЛАДКА: super_system_tool")
    
    if not IMPORT_OK:
        return
    
    results = {}
    
    # Тесты
    tests = [
        ("system_info", test_system_info),
        ("resource_usage", test_resource_usage),
        ("file_operations", test_file_operations),
        ("processes", test_processes)
    ]
    
    for test_name, test_func in tests:
        print(f"\n{'='*30}")
        print(f"ТЕСТ: {test_name}")
        try:
            result = test_func()
            results[test_name] = is_result_honest(result, test_name)
        except Exception as e:
            print(f"❌ ТЕСТ ОШИБКА: {e}")
            results[test_name] = False
    
    # Итоги
    print(f"\n{'='*50}")
    print("📊 ИТОГИ:")
    
    total_tests = len(results)
    passed_tests = sum(1 for success in results.values() if success)
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    print(f"Всего тестов: {total_tests}")
    print(f"Прошло тестов: {passed_tests}")
    print(f"Процент успеха: {success_rate:.1f}%")
    
    for test_name, success in results.items():
        status = "✅ ПРОШЕЛ" if success else "❌ ПРОВАЛЕН"
        print(f"  {test_name}: {status}")
    
    print(f"\n📊 Статус: {'✅ РАБОТАЕТ' if success_rate >= 75 else '❌ НЕ РАБОТАЕТ'}")

if __name__ == "__main__":
    main() 