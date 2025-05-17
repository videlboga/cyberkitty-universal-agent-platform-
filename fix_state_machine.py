#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для создания патча и применения к файлу state_machine.py в Docker-контейнере
"""

import os
import sys
import tempfile
import subprocess
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/patch_state_machine.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Содержимое патча для state_machine.py
PATCH_CONTENT = '''
def safe_compare(a, b, op):
    """
    Безопасное сравнение значений разных типов
    """
    # Пытаемся привести оба значения к одному типу
    try:
        # Если оба значения можно преобразовать в числа, делаем это
        a_float = float(a) if isinstance(a, (int, float, str)) and str(a).strip() else 0
        b_float = float(b) if isinstance(b, (int, float, str)) and str(b).strip() else 0
        
        if op == "==":
            return a_float == b_float
        elif op == "!=":
            return a_float != b_float
        elif op == "<":
            return a_float < b_float
        elif op == "<=":
            return a_float <= b_float
        elif op == ">":
            return a_float > b_float
        elif op == ">=":
            return a_float >= b_float
    except (ValueError, TypeError):
        # Если не удалось преобразовать в числа, сравниваем как строки
        a_str = str(a)
        b_str = str(b)
        
        if op == "==":
            return a_str == b_str
        elif op == "!=":
            return a_str != b_str
        elif op == "<":
            return a_str < b_str
        elif op == "<=":
            return a_str <= b_str
        elif op == ">":
            return a_str > b_str
        elif op == ">=":
            return a_str >= b_str
'''

# Функция для получения содержимого файла из контейнера
def get_file_content_from_container(container_name, file_path):
    """Получает содержимое файла из Docker-контейнера"""
    try:
        result = subprocess.run(
            ["docker", "exec", container_name, "cat", file_path],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f"Ошибка при получении содержимого файла: {e}")
        print(f"Ошибка: {e.stderr}")
        sys.exit(1)

# Функция для модификации файла state_machine.py
def modify_state_machine_file(content):
    """
    Модифицирует содержимое файла state_machine.py для исправления ошибок типов
    """
    # Проверяем, существует ли уже функция safe_compare в файле
    if "def safe_compare(" in content:
        logger.info("Функция safe_compare уже существует в файле")
        return content
    
    # Находим место для вставки кода (перед классом ScenarioStateMachine)
    if "class ScenarioStateMachine" in content:
        lines = content.split("\n")
        modified_lines = []
        
        for i, line in enumerate(lines):
            modified_lines.append(line)
            if line.strip().startswith("class ScenarioStateMachine"):
                # Вставляем функцию safe_compare перед классом
                logger.info("Добавляем функцию safe_compare перед классом ScenarioStateMachine")
                modified_lines.insert(i, PATCH_CONTENT)
                break
        
        # Модифицируем метод next_step для использования safe_compare
        in_next_step = False
        next_step_indentation = ""
        
        for i, line in enumerate(modified_lines):
            if line.strip().startswith("def next_step("):
                in_next_step = True
                next_step_indentation = line[:line.find("def")]
            
            # Для каждого условия с оператором сравнения в методе next_step
            if in_next_step and "<=" in line:
                # Находим строки, где выполняется eval с условиями
                if "eval(" in line and "condition" in line:
                    spaces_before = len(line) - len(line.lstrip())
                    indent = " " * spaces_before
                    
                    # Заменяем eval на безопасную версию
                    old_line = line
                    new_line = line.replace("eval(", "safe_eval(")
                    
                    if old_line != new_line:
                        logger.info(f"Заменяем eval на safe_eval в строке: {line.strip()}")
                        modified_lines[i] = new_line
                        
                        # Добавляем функцию safe_eval, если её ещё нет
                        if "def safe_eval(" not in content:
                            safe_eval_function = f"""
{indent}# Безопасное преобразование типов для сравнения
{indent}def safe_eval(expr, context):
{indent}    # Создаем безопасную среду для выполнения выражения
{indent}    safe_globals = {{"__builtins__": {{}}}}
{indent}    
{indent}    # Используем функцию безопасного сравнения
{indent}    safe_context = {{}}
{indent}    for key, value in context.items():
{indent}        safe_context[key] = value
{indent}    
{indent}    # Добавляем функцию безопасного сравнения в контекст
{indent}    safe_context["safe_compare"] = safe_compare
{indent}    
{indent}    # Заменяем операторы сравнения на вызовы safe_compare
{indent}    if "<=" in expr:
{indent}        parts = expr.split("<=")
{indent}        if len(parts) == 2:
{indent}            left = parts[0].strip()
{indent}            right = parts[1].strip()
{indent}            if left.startswith("context[") and right.startswith("context["):
{indent}                left_key = left[8:-1].strip('"\\\'')
{indent}                right_key = right[8:-1].strip('"\\\'')
{indent}                return safe_compare(context.get(left_key), context.get(right_key), "<=")
{indent}            elif left.startswith("context["):
{indent}                left_key = left[8:-1].strip('"\\\'')
{indent}                return safe_compare(context.get(left_key), eval(right, safe_globals, safe_context), "<=")
{indent}            elif right.startswith("context["):
{indent}                right_key = right[8:-1].strip('"\\\'')
{indent}                return safe_compare(eval(left, safe_globals, safe_context), context.get(right_key), "<=")
{indent}    
{indent}    # Если не удалось обработать выражение специальным образом, 
{indent}    # используем стандартный eval с безопасным контекстом
{indent}    return eval(expr, safe_globals, safe_context)
"""
                            # Вставляем функцию safe_eval
                            modified_lines.insert(i, safe_eval_function)
                            logger.info("Добавляем функцию safe_eval")
            
            # Выходим из метода next_step
            elif in_next_step and line.strip().startswith("def ") and "next_step" not in line:
                in_next_step = False
        
        return "\n".join(modified_lines)
    else:
        logger.error("Не найден класс ScenarioStateMachine в файле")
        return content

# Функция для обновления файла в контейнере
def update_file_in_container(container_name, file_path, content):
    """Обновляет файл в Docker-контейнере"""
    try:
        # Создаем временный файл для измененного содержимого
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp_file:
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        # Копируем временный файл в контейнер
        logger.info(f"Копируем файл в контейнер {container_name}:{file_path}")
        subprocess.run(
            ["docker", "cp", tmp_path, f"{container_name}:{file_path}"],
            check=True
        )
        
        # Удаляем временный файл
        os.remove(tmp_path)
        
        logger.info("Файл успешно обновлен в контейнере")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Ошибка при обновлении файла в контейнере: {e}")
        print(f"Ошибка: {e.stderr if hasattr(e, 'stderr') else str(e)}")
        return False

def main():
    # Проверяем наличие директории logs
    if not os.path.exists('logs'):
        os.makedirs('logs')
        logger.info("Создана директория logs")
    
    container_name = "universal_agent_system_app_1"
    file_path = "/app/app/core/state_machine.py"
    
    # Получаем текущее содержимое файла
    logger.info(f"Получаем содержимое файла {file_path} из контейнера {container_name}")
    content = get_file_content_from_container(container_name, file_path)
    
    # Модифицируем содержимое файла
    logger.info("Модифицируем содержимое файла")
    modified_content = modify_state_machine_file(content)
    
    # Если содержимое изменилось, обновляем файл в контейнере
    if content != modified_content:
        logger.info("Содержимое файла было изменено, обновляем файл в контейнере")
        if update_file_in_container(container_name, file_path, modified_content):
            print("Файл state_machine.py успешно обновлен в контейнере")
            logger.info("Файл state_machine.py успешно обновлен в контейнере")
            
            # Перезапускаем приложение в контейнере
            logger.info("Перезапускаем приложение в контейнере")
            try:
                subprocess.run(
                    ["docker", "exec", container_name, "sh", "-c", "kill -HUP 1"],
                    check=True
                )
                print("Приложение успешно перезапущено")
                logger.info("Приложение успешно перезапущено")
            except subprocess.CalledProcessError as e:
                logger.error(f"Ошибка при перезапуске приложения: {e}")
                print(f"Ошибка при перезапуске приложения: {e}")
                return False
        else:
            print("Ошибка при обновлении файла в контейнере")
            return False
    else:
        logger.info("Содержимое файла не изменилось")
        print("Файл state_machine.py не требует обновления")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 