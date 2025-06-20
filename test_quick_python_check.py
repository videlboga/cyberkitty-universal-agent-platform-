#!/usr/bin/env python3

from kittycore.tools.code_execution_tools import CodeExecutionTool

tool = CodeExecutionTool()

python_code = """
import math
result = math.sqrt(16)
print(f"Результат: {result}")
numbers = [1, 2, 3]
print(f"Сумма: {sum(numbers)}")
"""

result = tool.execute(
    action="execute_python",
    code=python_code,
    timeout=10
)

if result.success:
    print("✅ Код выполнен!")
    data = result.data
    output = data.get('output', '')
    print(f"Вывод программы:\n{output}")
    
    # Проверяем математические результаты
    if "4.0" in output and "6" in output:
        print("✅ Реальные математические вычисления найдены!")
    else:
        print("❌ Математические результаты не найдены")
else:
    print(f"❌ Ошибка: {result.error}") 