#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для исправления файла llm_plugin.py в Docker-контейнере
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
        logging.FileHandler('logs/patch_llm_plugin.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

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

# Функция для модификации файла llm_plugin.py
def modify_llm_plugin_file(content):
    """
    Модифицирует содержимое файла llm_plugin.py для исправления ошибки инициализации
    когда config равен None
    """
    # Ищем метод __init__ с ошибкой
    if "def __init__" in content and "self.api_key = config.get" in content:
        # Заменяем строку с ошибкой на проверку config на None
        lines = content.split("\n")
        modified_lines = []
        
        for line in lines:
            if "self.api_key = config.get('api_key')" in line:
                # Заменяем на проверку config на None
                indent = line[:line.find("self")]
                modified_line = f"{indent}self.api_key = config.get('api_key') if config else None or os.getenv(\"OPENROUTER_API_KEY\", \"\")"
                modified_lines.append(modified_line)
                logger.info(f"Заменили строку: {line.strip()} на {modified_line.strip()}")
            else:
                modified_lines.append(line)
        
        modified_content = "\n".join(modified_lines)
        logger.info("Файл llm_plugin.py успешно модифицирован")
        return modified_content
    else:
        logger.warning("Не найдена строка с ошибкой в файле llm_plugin.py")
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
    
    # Перезапускаем контейнер чтобы получить к нему доступ
    logger.info("Перезапускаем контейнер app")
    subprocess.run(
        ["docker-compose", "up", "-d", "app"],
        check=True
    )
    
    # Небольшая пауза чтобы контейнер успел запуститься
    import time
    time.sleep(2)
    
    container_name = "universal_agent_system_app_1"
    file_path = "/app/app/plugins/llm_plugin.py"
    
    try:
        # Останавливаем приложение в контейнере чтобы не конфликтовало с обновлением файлов
        logger.info("Останавливаем uvicorn в контейнере")
        subprocess.run(
            ["docker", "exec", container_name, "pkill", "-f", "uvicorn"],
            check=False  # Игнорируем ошибки, так как процесс может быть уже не запущен
        )
        
        # Получаем текущее содержимое файла
        logger.info(f"Получаем содержимое файла {file_path} из контейнера {container_name}")
        content = get_file_content_from_container(container_name, file_path)
        
        # Модифицируем содержимое файла
        logger.info("Модифицируем содержимое файла")
        modified_content = modify_llm_plugin_file(content)
        
        # Если содержимое изменилось, обновляем файл в контейнере
        if content != modified_content:
            logger.info("Содержимое файла было изменено, обновляем файл в контейнере")
            if update_file_in_container(container_name, file_path, modified_content):
                print("Файл llm_plugin.py успешно обновлен в контейнере")
                logger.info("Файл llm_plugin.py успешно обновлен в контейнере")
                
                # Теперь нужно исправить state_machine.py
                state_machine_path = "/app/app/core/state_machine.py"
                logger.info(f"Получаем содержимое файла {state_machine_path} из контейнера {container_name}")
                
                try:
                    state_machine_content = get_file_content_from_container(container_name, state_machine_path)
                    
                    # Добавляем функцию safe_compare для безопасного сравнения типов
                    if "def safe_compare" not in state_machine_content:
                        # Находим класс ScenarioStateMachine
                        if "class ScenarioStateMachine" in state_machine_content:
                            # Добавляем функцию перед классом
                            safe_compare_code = """
def safe_compare(a, b, op):
    '''
    Безопасное сравнение значений разных типов
    '''
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
"""
                            parts = state_machine_content.split("class ScenarioStateMachine")
                            modified_state_machine = parts[0] + safe_compare_code + "\nclass ScenarioStateMachine" + parts[1]
                            
                            # Также найдем метод next_step и добавим safe_eval
                            if "def next_step" in modified_state_machine and "eval(condition" in modified_state_machine:
                                parts = modified_state_machine.split("def next_step")
                                method_part = parts[1]
                                
                                # Разбиваем метод next_step
                                lines = method_part.split("\n")
                                in_condition_block = False
                                safe_eval_added = False
                                next_indent = ""
                                
                                for i, line in enumerate(lines):
                                    if "eval(condition" in line:
                                        indent = line[:line.find("eval")]
                                        next_indent = indent
                                        in_condition_block = True
                                        lines[i] = line.replace("eval(condition", "safe_eval(condition")
                                    
                                    if in_condition_block and not safe_eval_added and line.strip().startswith("def "):
                                        # Добавляем safe_eval перед следующим методом
                                        safe_eval_code = f"""
{next_indent}def safe_eval(expr, context):
{next_indent}    '''
{next_indent}    Создаем безопасную среду для выполнения выражения
{next_indent}    '''
{next_indent}    safe_globals = {{"__builtins__": {{}}}}
{next_indent}    
{next_indent}    # Используем функцию безопасного сравнения
{next_indent}    safe_context = {{}}
{next_indent}    for key, value in context.items():
{next_indent}        safe_context[key] = value
{next_indent}    
{next_indent}    # Добавляем функцию безопасного сравнения в контекст
{next_indent}    safe_context["safe_compare"] = safe_compare
{next_indent}    
{next_indent}    # Заменяем операторы сравнения на вызовы safe_compare
{next_indent}    if "<=" in expr:
{next_indent}        parts = expr.split("<=")
{next_indent}        if len(parts) == 2:
{next_indent}            left = parts[0].strip()
{next_indent}            right = parts[1].strip()
{next_indent}            if left.startswith("context[") and right.startswith("context["):
{next_indent}                left_key = left[8:-1].strip('"\\\'')
{next_indent}                right_key = right[8:-1].strip('"\\\'')
{next_indent}                return safe_compare(context.get(left_key), context.get(right_key), "<=")
{next_indent}            elif left.startswith("context["):
{next_indent}                left_key = left[8:-1].strip('"\\\'')
{next_indent}                return safe_compare(context.get(left_key), eval(right, safe_globals, safe_context), "<=")
{next_indent}            elif right.startswith("context["):
{next_indent}                right_key = right[8:-1].strip('"\\\'')
{next_indent}                return safe_compare(eval(left, safe_globals, safe_context), context.get(right_key), "<=")
{next_indent}    
{next_indent}    # Если не удалось обработать выражение специальным образом, 
{next_indent}    # используем стандартный eval с безопасным контекстом
{next_indent}    return eval(expr, safe_globals, safe_context)
"""
                                        # Вставляем функцию safe_eval
                                        lines.insert(i, safe_eval_code)
                                        safe_eval_added = True
                                        break
                                
                                method_part = "\n".join(lines)
                                modified_state_machine = parts[0] + "def next_step" + method_part
                            
                            # Обновляем state_machine.py
                            logger.info("Обновляем state_machine.py")
                            if update_file_in_container(container_name, state_machine_path, modified_state_machine):
                                print("Файл state_machine.py успешно обновлен в контейнере")
                                logger.info("Файл state_machine.py успешно обновлен в контейнере")
                            else:
                                print("Ошибка при обновлении файла state_machine.py в контейнере")
                                logger.error("Ошибка при обновлении файла state_machine.py в контейнере")
                        else:
                            logger.warning("Не найден класс ScenarioStateMachine в файле state_machine.py")
                    else:
                        logger.info("Функция safe_compare уже существует в файле state_machine.py")
                
                except Exception as e:
                    logger.error(f"Ошибка при обработке файла state_machine.py: {e}")
                    print(f"Ошибка при обработке файла state_machine.py: {e}")
                
                # Перезапускаем контейнер чтобы применить изменения
                logger.info("Перезапускаем контейнер app")
                subprocess.run(
                    ["docker-compose", "restart", "app"],
                    check=True
                )
                
                print("Контейнер app успешно перезапущен с обновленными файлами")
                logger.info("Контейнер app успешно перезапущен с обновленными файлами")
            else:
                print("Ошибка при обновлении файла llm_plugin.py в контейнере")
                return False
        else:
            logger.info("Содержимое файла llm_plugin.py не изменилось")
            print("Файл llm_plugin.py не требует обновления")
        
        return True
    except Exception as e:
        logger.error(f"Ошибка при выполнении скрипта: {e}")
        print(f"Ошибка: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 