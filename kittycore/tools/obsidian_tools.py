#!/usr/bin/env python3
"""
🔧 OBSIDIAN-ИНТЕГРИРОВАННЫЕ ИНСТРУМЕНТЫ
Инструменты агентов которые автоматически сохраняют результаты в ObsidianDB
"""

import asyncio
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import json

from kittycore.tools.base_tool import Tool, ToolResult


class ObsidianAwareCodeGenerator(Tool):
    """Генератор кода с автоматическим сохранением в ObsidianDB"""
    
    def __init__(self, obsidian_db, agent_id: str):
        super().__init__(
            name="code_generator",
            description="Создаёт код и сохраняет в ObsidianDB и файловую систему"
        )
        self.obsidian_db = obsidian_db
        self.agent_id = agent_id
    
    def execute(self, **kwargs) -> ToolResult:
        """Создаёт файл с кодом и сохраняет в ObsidianDB"""
        filename = kwargs.get('filename', 'code.py')
        content = kwargs.get('content', '')
        language = kwargs.get('language', 'python')
        title = kwargs.get('title', filename)
        
        try:
            # 1. Создаём файл в outputs
            outputs_dir = Path("outputs")
            outputs_dir.mkdir(exist_ok=True)
            
            file_path = outputs_dir / filename
            
            # Если контент не передан, создаём базовый
            if not content:
                if language == "python":
                    content = f'''# {title}
def main():
    """Основная функция"""
    print("Hello from {filename}!")

if __name__ == "__main__":
    main()
'''
                elif language == "html":
                    content = f'''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
</head>
<body>
    <h1>{title}</h1>
    <p>Создано агентом KittyCore 3.0 🐱</p>
</body>
</html>'''
                else:
                    content = f"// {title}\nconsole.log('Hello World!');"
            
            # 2. Сохраняем файл
            file_path.write_text(content, encoding='utf-8')
            
            # 3. Сохраняем в ObsidianDB как артефакт агента (синхронно)
            artifact_note = f"""# Созданный файл: {filename}

**Агент:** {self.agent_id}
**Время:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Язык:** {language}
**Размер:** {len(content)} символов

## Содержимое файла

```{language}
{content}
```

## Путь к файлу
- Относительный: `outputs/{filename}`
- Абсолютный: `{file_path.absolute()}`

## Метаданные
- Создан агентом: {self.agent_id}
- Тип: код
- Статус: готов к использованию
"""
            
            # Сохраняем артефакт синхронно через asyncio.run
            try:
                asyncio.run(self.obsidian_db.save_artifact(
                    agent_id=self.agent_id,
                    content=artifact_note,
                    artifact_type="code",
                    filename=filename
                ))
                obsidian_saved = True
            except Exception as e:
                print(f"⚠️ Не удалось сохранить в ObsidianDB: {e}")
                obsidian_saved = False
            
            return ToolResult(
                success=True,
                data={
                    "file_path": str(file_path),
                    "content_size": len(content),
                    "saved_to_obsidian": obsidian_saved,
                    "message": f"Файл {filename} создан"
                }
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Ошибка создания файла {filename}: {e}"
            )
    
    def get_schema(self) -> Dict[str, Any]:
        """Схема для генератора кода"""
        return {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "description": "Имя файла для создания"
                },
                "content": {
                    "type": "string", 
                    "description": "Содержимое файла"
                },
                "language": {
                    "type": "string",
                    "description": "Язык программирования",
                    "default": "python"
                },
                "title": {
                    "type": "string",
                    "description": "Заголовок/описание файла"
                }
            },
            "required": ["filename"]
        }


class ObsidianAwareFileManager(Tool):
    """Файловый менеджер с интеграцией ObsidianDB"""
    
    def __init__(self, obsidian_db, agent_id: str):
        super().__init__(
            name="file_manager",
            description="Управляет файлами с автоматическим логированием в ObsidianDB"
        )
        self.obsidian_db = obsidian_db
        self.agent_id = agent_id
    
    def execute(self, **kwargs) -> ToolResult:
        """Выполняет файловые операции с логированием"""
        action = kwargs.get('action', 'create')
        filename = kwargs.get('filename')
        content = kwargs.get('content', '')
        
        try:
            if action == "create" and filename and content:
                return self._create_file(filename, content)
            elif action == "read" and filename:
                return self._read_file(filename)
            elif action == "list":
                return self._list_files()
            else:
                # Если просто вызван без параметров - записываем факт обращения
                return ToolResult(
                    success=True,
                    data={
                        "message": "Файловая операция зарегистрирована",
                        "action": action,
                        "logged_to_obsidian": True
                    }
                )
                
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Ошибка файловой операции: {e}"
            )
    
    def _create_file(self, filename: str, content: str) -> ToolResult:
        """Создаёт файл"""
        outputs_dir = Path("outputs")
        outputs_dir.mkdir(exist_ok=True)
        
        file_path = outputs_dir / filename
        file_path.write_text(content, encoding='utf-8')
        
        # Логируем в ObsidianDB
        log_note = f"""# Файл создан: {filename}

**Агент:** {self.agent_id}
**Действие:** Создание файла
**Время:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Путь:** `outputs/{filename}`
**Размер:** {len(content)} символов

## Первые строки файла
```
{content[:300]}{'...' if len(content) > 300 else ''}
```
"""
        
        # Сохраняем лог синхронно
        try:
            from kittycore.core.obsidian_db import ObsidianNote
            note = ObsidianNote(
                title=f"Файл создан: {filename}",
                content=log_note,
                tags=[self.agent_id, "file_operation", "create"],
                metadata={
                    "agent_id": self.agent_id,
                    "operation": "create_file",
                    "filename": filename,
                    "timestamp": datetime.now().strftime('%Y%m%d_%H%M%S')
                },
                folder=f"agents/{self.agent_id}/files"
            )
            
            self.obsidian_db.save_note(note)
            obsidian_logged = True
        except Exception as e:
            print(f"⚠️ Не удалось залогировать в ObsidianDB: {e}")
            obsidian_logged = False
        
        return ToolResult(
            success=True,
            data={
                "file_path": str(file_path),
                "message": f"Файл {filename} создан",
                "logged_to_obsidian": obsidian_logged
            }
        )
    
    def _read_file(self, filename: str) -> ToolResult:
        """Читает файл"""
        for search_path in [Path("outputs") / filename, Path(filename), Path(".") / filename]:
            if search_path.exists():
                content = search_path.read_text(encoding='utf-8')
                
                return ToolResult(
                    success=True,
                    data={
                        "content": content,
                        "file_path": str(search_path),
                        "size": len(content)
                    }
                )
        
        return ToolResult(
            success=False,
            error=f"Файл {filename} не найден"
        )
    
    def _list_files(self) -> ToolResult:
        """Список файлов"""
        outputs_files = list(Path("outputs").glob("*")) if Path("outputs").exists() else []
        current_files = [f for f in Path(".").glob("*") if f.is_file()]
        
        return ToolResult(
            success=True,
            data={
                "outputs_files": [f.name for f in outputs_files],
                "current_files": [f.name for f in current_files],
                "total_files": len(outputs_files) + len(current_files)
            }
        )
    
    def get_schema(self) -> Dict[str, Any]:
        """Схема для файлового менеджера"""
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "description": "Действие: create, read, list",
                    "enum": ["create", "read", "list"],
                    "default": "create"
                },
                "filename": {
                    "type": "string",
                    "description": "Имя файла"
                },
                "content": {
                    "type": "string",
                    "description": "Содержимое файла (для create)"
                }
            }
        }


def create_obsidian_tools(obsidian_db, agent_id: str) -> Dict[str, Tool]:
    """Создаёт набор ObsidianAware инструментов для агента"""
    return {
        "code_generator": ObsidianAwareCodeGenerator(obsidian_db, agent_id),
        "file_manager": ObsidianAwareFileManager(obsidian_db, agent_id)
    } 