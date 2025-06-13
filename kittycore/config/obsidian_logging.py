"""
🗄️ OBSIDIAN LOGGING SYSTEM
Система логирования в Obsidian vault как markdown файлы
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
from loguru import logger

class ObsidianLogHandler:
    """Обработчик логов для сохранения в Obsidian vault"""
    
    def __init__(self, vault_path: str = "./obsidian_vault"):
        self.vault_path = Path(vault_path)
        self.logs_folder = self.vault_path / "system" / "logs"
        self.logs_folder.mkdir(parents=True, exist_ok=True)
        
        # Файлы логов в markdown формате
        self.log_files = {
            "orchestrator": self.logs_folder / "🧭 Orchestrator Logs.md",
            "agents": self.logs_folder / "🤖 Agents Logs.md", 
            "memory": self.logs_folder / "🧠 Memory Logs.md",
            "human": self.logs_folder / "👤 Human Collaboration Logs.md",
            "improvement": self.logs_folder / "🔄 Iterative Improvement Logs.md",
            "system": self.logs_folder / "⚙️ System Logs.md",
            "errors": self.logs_folder / "❌ Error Logs.md"
        }
        
        # Создаём файлы если их нет
        for log_type, log_file in self.log_files.items():
            if not log_file.exists():
                self._create_log_file(log_file, log_type)
    
    def _create_log_file(self, log_file: Path, log_type: str):
        """Создаёт новый файл лога с заголовком"""
        
        headers = {
            "orchestrator": "🧭 Логи Оркестратора",
            "agents": "🤖 Логи Агентов",
            "memory": "🧠 Логи Памяти", 
            "human": "👤 Логи Человеческого Вмешательства",
            "improvement": "🔄 Логи Итеративного Улучшения",
            "system": "⚙️ Системные Логи",
            "errors": "❌ Логи Ошибок"
        }
        
        content = f"""---
title: {headers.get(log_type, log_type.title())}
type: system_log
category: {log_type}
created: {datetime.now().isoformat()}
tags: [kittycore, logs, {log_type}]
---

# {headers.get(log_type, log_type.title())}

Автоматически генерируемые логи KittyCore 3.0

---

"""
        
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def write_log(self, message):
        """Записывает лог в соответствующий markdown файл"""
        
        # Loguru передаёт Message объект, а не dict
        # Извлекаем данные из record
        if hasattr(message, 'record'):
            record = message.record
        else:
            # Fallback для совместимости
            record = message
        
        # Определяем тип лога по имени модуля
        module_name = record.get("name", "").lower() if isinstance(record, dict) else getattr(record, 'name', '').lower()
        log_type = "system"  # по умолчанию
        
        if "orchestrator" in module_name:
            log_type = "orchestrator"
        elif any(keyword in module_name for keyword in ["agent", "factory", "intellectual"]):
            log_type = "agents"
        elif "memory" in module_name:
            log_type = "memory"
        elif any(keyword in module_name for keyword in ["human", "collaboration", "obsidian"]):
            log_type = "human"
        elif any(keyword in module_name for keyword in ["improvement", "validator", "fixer"]):
            log_type = "improvement"
        elif record.get("level", {}).get("name") == "ERROR":
            log_type = "errors"
        
        log_file = self.log_files[log_type]
        
        # Форматируем запись лога
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        
        if isinstance(record, dict):
            level = record.get("level", {}).get("name", "INFO")
            log_message = record.get("message", "")
            function = record.get("function", "")
            line = record.get("line", "")
        else:
            level = getattr(record.level, 'name', 'INFO') if hasattr(record, 'level') else 'INFO'
            log_message = str(record.message) if hasattr(record, 'message') else str(record)
            function = getattr(record, 'function', '') if hasattr(record, 'function') else ''
            line = getattr(record, 'line', '') if hasattr(record, 'line') else ''
        
        # Создаём markdown запись
        log_entry = f"""
## {timestamp} | {level}

**Модуль:** `{module_name}`  
**Функция:** `{function}:{line}`  
**Сообщение:** {log_message}

"""
        
        # Добавляем исключение если есть
        exception = record.get("exception") if isinstance(record, dict) else getattr(record, 'exception', None)
        if exception:
            log_entry += f"""
**Исключение:**
```
{exception}
```

"""
        
        # Добавляем разделитель
        log_entry += "---\n"
        
        # Записываем в файл
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
        except Exception as e:
            # Fallback в консоль если не можем записать в файл
            print(f"❌ Ошибка записи лога в {log_file}: {e}")

def setup_obsidian_logging(vault_path: str = "./obsidian_vault"):
    """Настраивает логирование в Obsidian vault"""
    
    # Удаляем стандартные обработчики
    logger.remove()
    
    # Создаём обработчик для Obsidian
    obsidian_handler = ObsidianLogHandler(vault_path)
    
    # Консольный вывод (для разработки)
    logger.add(
        sys.stderr,
        level="INFO",
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True
    )
    
    # Obsidian markdown логи
    logger.add(
        obsidian_handler.write_log,
        level="INFO",
        format="{time} | {level} | {name}:{function}:{line} | {message}",
        serialize=True
    )
    
    logger.info("🗄️ Система логирования в Obsidian vault настроена")
    logger.info(f"📁 Логи сохраняются в: {obsidian_handler.logs_folder}")

# Автоматическая настройка при импорте
setup_obsidian_logging() 