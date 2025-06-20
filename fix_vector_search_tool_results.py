#!/usr/bin/env python3
"""
🔧 МАССОВОЕ ИСПРАВЛЕНИЕ: vector_search_tool.py ToolResult

Убираем неправильные параметры message и tool_name из всех ToolResult
"""

import re

def fix_vector_search_tool():
    """Исправить все ToolResult в vector_search_tool.py"""
    
    # Читаем файл
    with open('kittycore/tools/vector_search_tool.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"📄 Исходный размер файла: {len(content)} символов")
    
    # Паттерн для поиска ToolResult с неправильными параметрами
    # Заменяем message=... и tool_name=... на пустые строки
    pattern1 = r',\s*message=f?"[^"]*"[^,)]*'
    pattern2 = r',\s*tool_name=[^,)]*'
    
    # Убираем message параметры
    content = re.sub(pattern1, '', content)
    print("✅ Удалены все message параметры")
    
    # Убираем tool_name параметры  
    content = re.sub(pattern2, '', content)
    print("✅ Удалены все tool_name параметры")
    
    # Специальная очистка оставшихся случаев
    lines = content.split('\n')
    fixed_lines = []
    
    for line in lines:
        # Если строка содержит message= или tool_name=, пропускаем
        if 'message=' in line or 'tool_name=' in line:
            print(f"🗑️ Удаляем строку: {line.strip()}")
            continue
        fixed_lines.append(line)
    
    content = '\n'.join(fixed_lines)
    
    print(f"📄 Исправленный размер файла: {len(content)} символов")
    
    # Записываем обратно
    with open('kittycore/tools/vector_search_tool.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Файл vector_search_tool.py исправлен!")

if __name__ == "__main__":
    fix_vector_search_tool() 