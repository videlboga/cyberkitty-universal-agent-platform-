#!/usr/bin/env python3
"""
📄 ОТЛАДКА: document_tool
"""

import asyncio
import time
import json
import tempfile
import os

try:
    from kittycore.tools.document_tool_unified import DocumentTool
    IMPORT_OK = True
    print("✅ Импорт document_tool успешен")
except ImportError as e:
    print(f"❌ ИМПОРТ ОШИБКА: {e}")
    IMPORT_OK = False

async def test_text_document():
    """Тест обработки текстового документа"""
    if not IMPORT_OK:
        return "IMPORT_ERROR"
    
    print("\n📄 Тестирую обработку текстового документа...")
    tool = DocumentTool()
    
    # Создаем временный текстовый файл
    test_content = """
Тест документа для DocumentTool
================================

Это тестовый документ с различными элементами:

1. Заголовки
2. Списки  
3. Обычный текст

## Секция 2

Дополнительный контент для проверки извлечения текста.
Несколько строк текста для тестирования.

### Числа и данные
- Цена: 1000 рублей
- Количество: 5 штук
- Процент: 95%
"""
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as f:
        temp_path = f.name
        f.write(test_content)
    
    try:
        # ВАЖНО: DocumentTool асинхронный - используем await
        result = await tool.execute({
            'action': 'extract_text',
            'file_path': temp_path,
            'filename': 'test_document.txt'
        })
        
        print(f"📊 Результат: {type(result)}")
        
        if isinstance(result, dict):
            success = result.get('success', False)
            print(f"✅ Success: {success}")
            
            if success:
                text = result.get('text', '')
                print(f"📦 Размер извлеченного текста: {len(text)} символов")
                
                # Проверяем, что ключевые фразы присутствуют
                key_phrases = ["Тест документа", "DocumentTool", "1000 рублей", "95%"]
                found_phrases = [phrase for phrase in key_phrases if phrase in text]
                print(f"🔑 Найдено ключевых фраз: {len(found_phrases)}/{len(key_phrases)}")
                print(f"   Фразы: {found_phrases}")
                
                # Проверяем метаданные
                metadata = result.get('metadata', {})
                if metadata:
                    print(f"📋 Метаданные: {list(metadata.keys()) if isinstance(metadata, dict) else 'не dict'}")
            else:
                error = result.get('error', 'НЕИЗВЕСТНО')
                print(f"❌ Ошибка: {error}")
        
        return result
        
    finally:
        # Удаляем временный файл
        try:
            os.unlink(temp_path)
        except:
            pass

async def test_supported_formats():
    """Тест получения поддерживаемых форматов"""
    if not IMPORT_OK:
        return "IMPORT_ERROR"
    
    print("\n📋 Тестирую поддерживаемые форматы...")
    tool = DocumentTool()
    
    result = await tool.execute({
        'action': 'get_supported_formats'
    })
    
    print(f"📊 Результат: {type(result)}")
    if isinstance(result, dict):
        success = result.get('success', False)
        print(f"✅ Success: {success}")
        
        if success:
            formats = result.get('supported_formats', [])
            print(f"📄 Поддерживаемых форматов: {len(formats)}")
            if formats:
                print(f"   Форматы: {formats[:5]}...")  # Первые 5
    
    return result

async def test_tool_info():
    """Тест получения информации об инструменте"""
    if not IMPORT_OK:
        return "IMPORT_ERROR"
    
    print("\n📋 Тестирую информацию об инструменте...")
    tool = DocumentTool()
    
    result = await tool.execute({
        'action': 'get_info'
    })
    
    print(f"📊 Результат: {type(result)}")
    if isinstance(result, dict):
        success = result.get('success', False)
        print(f"✅ Success: {success}")
        
        if success:
            info = result.get('info', {})
            if isinstance(info, dict):
                print(f"📄 Информация: {list(info.keys())}")
    
    return result

async def test_json_document():
    """Тест обработки JSON документа"""
    if not IMPORT_OK:
        return "IMPORT_ERROR"
    
    print("\n📄 Тестирую обработку JSON документа...")
    tool = DocumentTool()
    
    # Создаем временный JSON файл
    test_json = {
        "project": "KittyCore 3.0",
        "version": "3.0.0",
        "tools": [
            {"name": "document_tool", "status": "testing"},
            {"name": "api_request_tool", "status": "working"}
        ],
        "stats": {
            "total_tools": 18,
            "tested_tools": 7,
            "success_rate": 93.0
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json', encoding='utf-8') as f:
        temp_path = f.name
        json.dump(test_json, f, ensure_ascii=False, indent=2)
    
    try:
        result = await tool.execute({
            'action': 'extract_text',
            'file_path': temp_path,
            'filename': 'test_data.json'
        })
        
        print(f"📊 JSON результат: {type(result)}")
        
        if isinstance(result, dict):
            success = result.get('success', False)
            print(f"✅ Success: {success}")
            
            if success:
                text = result.get('text', '')
                # Проверяем JSON содержимое
                json_phrases = ["KittyCore 3.0", "document_tool", "93.0"]
                found_json = [phrase for phrase in json_phrases if phrase in text]
                print(f"🔑 JSON данные найдены: {len(found_json)}/{len(json_phrases)}")
        
        return result
        
    finally:
        try:
            os.unlink(temp_path)
        except:
            pass

def is_result_honest(result, test_name):
    """Проверка честности результата"""
    if not result:
        print(f"❌ {test_name}: Пустой результат")
        return False
    
    if not isinstance(result, dict):
        print(f"❌ {test_name}: Результат не словарь")
        return False
    
    success = result.get('success', False)
    if not success:
        print(f"❌ {test_name}: success=False")
        error = result.get('error', 'НЕИЗВЕСТНО')
        print(f"   Ошибка: {error}")
        return False
    
    data_str = str(result)
    data_size = len(data_str)
    
    # Проверка на фейковые паттерны
    fake_patterns = [
        "document_tool: успешно",
        "демо документ",
        "заглушка текста"
    ]
    
    for pattern in fake_patterns:
        if pattern.lower() in data_str.lower():
            print(f"❌ {test_name}: Найден фейковый паттерн: {pattern}")
            return False
    
    # Проверка на реальные признаки обработки документов
    doc_indicators = [
        "text", "content", "metadata", "format", "extract", 
        "тест документа", "kittycore", "document_tool", "поддерживаемых"
    ]
    
    has_doc_data = any(indicator.lower() in data_str.lower() for indicator in doc_indicators)
    
    if not has_doc_data:
        print(f"❌ {test_name}: Нет признаков реальной обработки документов")
        return False
    
    if data_size < 50:
        print(f"❌ {test_name}: Слишком маленький результат ({data_size} байт)")
        return False
    
    print(f"✅ {test_name}: ЧЕСТНЫЙ результат ({data_size} байт)")
    return True

async def main():
    print("📄 ОТЛАДКА: document_tool")
    
    if not IMPORT_OK:
        return
    
    results = {}
    
    # Тесты (все асинхронные)
    tests = [
        ("text_document", test_text_document),
        ("json_document", test_json_document),
        ("supported_formats", test_supported_formats),
        ("tool_info", test_tool_info)
    ]
    
    for test_name, test_func in tests:
        print(f"\n{'='*30}")
        print(f"ТЕСТ: {test_name}")
        try:
            result = await test_func()
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
    asyncio.run(main()) 