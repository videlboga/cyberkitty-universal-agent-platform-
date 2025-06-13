"""
🗄️ ПРОСТАЯ СИСТЕМА ЛОГИРОВАНИЯ В OBSIDIAN VAULT
"""

import sys
from pathlib import Path
from datetime import datetime
from loguru import logger

def simple_obsidian_sink(message):
    """Простой обработчик логов для Obsidian vault"""
    
    try:
        # Создаём папку логов
        vault_path = Path("./obsidian_vault")
        logs_folder = vault_path / "system" / "logs"
        logs_folder.mkdir(parents=True, exist_ok=True)
        
        # Определяем файл лога по модулю
        record = message.record
        module_name = record['name'].lower()
        
        if "improvement" in module_name or "validator" in module_name:
            log_file = logs_folder / "🔄 Iterative Improvement Logs.md"
        elif "orchestrator" in module_name:
            log_file = logs_folder / "🧭 Orchestrator Logs.md"
        elif "agent" in module_name:
            log_file = logs_folder / "🤖 Agents Logs.md"
        else:
            log_file = logs_folder / "⚙️ System Logs.md"
        
        # Создаём файл если его нет
        if not log_file.exists():
            header = f"""---
title: {log_file.stem}
type: system_log
created: {datetime.now().isoformat()}
tags: [kittycore, logs]
---

# {log_file.stem}

Автоматически генерируемые логи KittyCore 3.0

---

"""
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write(header)
        
        # Форматируем запись
        timestamp = record['time'].strftime("%H:%M:%S.%f")[:-3]
        level = record['level'].name
        function = record['function']
        line = record['line']
        log_message = record['message']
        
        # Создаём markdown запись
        log_entry = f"""
## {timestamp} | {level}

**Модуль:** `{module_name}`  
**Функция:** `{function}:{line}`  
**Сообщение:** {log_message}

---

"""
        
        # Записываем в файл
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
            
    except Exception as e:
        # Fallback в консоль
        print(f"❌ Ошибка записи лога: {e}")

def setup_simple_obsidian_logging():
    """Настраивает простое логирование в Obsidian vault"""
    
    # Удаляем стандартные обработчики
    logger.remove()
    
    # Консольный вывод
    logger.add(
        sys.stderr,
        level="INFO",
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True
    )
    
    # Obsidian markdown логи
    logger.add(
        simple_obsidian_sink,
        level="INFO",
        format="{time} | {level} | {name}:{function}:{line} | {message}"
    )
    
    logger.info("🗄️ Простая система логирования в Obsidian vault настроена")

# Автоматическая настройка при импорте
setup_simple_obsidian_logging() 