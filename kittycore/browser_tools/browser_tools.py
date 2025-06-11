"""
Browser Tools - Инструменты для разработки браузерных расширений

Включает автоматизацию браузера, работу с файлами, валидацию manifest и упаковку.
"""

import os
import json
import zipfile
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, List
import logging

# Импорт базового класса Tool из основного модуля
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from tools import Tool
from config import get_config

logger = logging.getLogger(__name__)


class FileSystemTool(Tool):
    """Инструмент для работы с файловой системой проекта"""
    
    def __init__(self):
        super().__init__(
            name="filesystem",
            description="Создание, чтение, запись и удаление файлов и папок проекта"
        )
    
    def execute(self, action: str, path: str, content: str = None, **kwargs):
        """
        Выполнить операцию с файловой системой
        
        Args:
            action: Действие (create, read, write, delete, mkdir, list)
            path: Путь к файлу или папке
            content: Содержимое для записи (если нужно)
        """
        from tools import ToolResult
        
        try:
            path = Path(path).resolve()
            
            if action == "read":
                if path.exists() and path.is_file():
                    content = path.read_text(encoding='utf-8')
                    return ToolResult(success=True, data={"content": content, "path": str(path)})
                return ToolResult(success=False, error=f"Файл {path} не найден")
            
            elif action == "write":
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content or "", encoding='utf-8')
                return ToolResult(success=True, data={"message": f"Файл {path} успешно записан", "path": str(path)})
            
            elif action == "create":
                path.parent.mkdir(parents=True, exist_ok=True)
                path.touch()
                if content:
                    path.write_text(content, encoding='utf-8')
                return ToolResult(success=True, data={"message": f"Файл {path} создан", "path": str(path)})
            
            elif action == "delete":
                if path.exists():
                    if path.is_file():
                        path.unlink()
                        return ToolResult(success=True, data={"message": f"Файл {path} удалён", "path": str(path)})
                    elif path.is_dir():
                        shutil.rmtree(path)
                        return ToolResult(success=True, data={"message": f"Папка {path} удалена", "path": str(path)})
                return ToolResult(success=False, error=f"Путь {path} не найден")
            
            elif action == "mkdir":
                path.mkdir(parents=True, exist_ok=True)
                return ToolResult(success=True, data={"message": f"Папка {path} создана", "path": str(path)})
            
            elif action == "list":
                if path.exists() and path.is_dir():
                    items = []
                    for item in path.iterdir():
                        item_type = "📁" if item.is_dir() else "📄"
                        items.append(f"{item_type} {item.name}")
                    return ToolResult(success=True, data={"items": items, "path": str(path)})
                return ToolResult(success=False, error=f"Папка {path} не найдена")
            
            else:
                return ToolResult(success=False, error=f"Неизвестное действие: {action}")
                
        except Exception as e:
            logger.error(f"Ошибка FileSystemTool: {e}")
            return ToolResult(success=False, error=str(e))
    
    def get_schema(self):
        """Схема для файловых операций"""
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["read", "write", "create", "delete", "mkdir", "list"],
                    "description": "Действие с файловой системой"
                },
                "path": {
                    "type": "string",
                    "description": "Путь к файлу или папке"
                },
                "content": {
                    "type": "string",
                    "description": "Содержимое для записи (опционально)"
                }
            },
            "required": ["action", "path"]
        }


class ManifestValidatorTool(Tool):
    """Инструмент для валидации manifest.json расширения"""
    
    def __init__(self):
        super().__init__(
            name="manifest_validator",
            description="Валидация manifest.json файлов браузерных расширений"
        )
        
        # Обязательные поля для Manifest V3
        self.required_fields_v3 = {
            "manifest_version": int,
            "name": str,
            "version": str
        }
        
        # Допустимые поля
        self.valid_fields = {
            "manifest_version", "name", "version", "description", "icons",
            "action", "background", "content_scripts", "permissions",
            "host_permissions", "web_accessible_resources", "content_security_policy",
            "options_page", "options_ui", "devtools_page", "minimum_chrome_version"
        }
    
    def execute(self, manifest_path: str, **kwargs):
        """
        Валидировать manifest.json файл
        
        Args:
            manifest_path: Путь к manifest.json
        """
        from tools import ToolResult
        
        try:
            path = Path(manifest_path)
            
            if not path.exists():
                return ToolResult(success=False, error=f"Файл {manifest_path} не найден")
            
            # Чтение и парсинг JSON
            try:
                manifest = json.loads(path.read_text(encoding='utf-8'))
            except json.JSONDecodeError as e:
                return ToolResult(success=False, error=f"Ошибка JSON синтаксиса: {e}")
            
            issues = []
            warnings = []
            
            # Проверка версии манифеста
            manifest_version = manifest.get("manifest_version")
            if manifest_version not in [2, 3]:
                issues.append("❌ manifest_version должен быть 2 или 3")
            elif manifest_version == 2:
                warnings.append("⚠️ Manifest V2 устарел, рекомендуется V3")
            
            # Проверка обязательных полей
            for field, field_type in self.required_fields_v3.items():
                if field not in manifest:
                    issues.append(f"❌ Отсутствует обязательное поле: {field}")
                elif not isinstance(manifest[field], field_type):
                    issues.append(f"❌ Неверный тип поля {field}, ожидается {field_type.__name__}")
            
            # Проверка версии
            version = manifest.get("version", "")
            if version and not self._is_valid_version(version):
                issues.append("❌ Неверный формат версии (ожидается x.y.z)")
            
            # Проверка permissions для V3
            if manifest_version == 3:
                if "permissions" in manifest:
                    self._validate_permissions_v3(manifest["permissions"], issues, warnings)
            
            # Проверка неизвестных полей
            for field in manifest:
                if field not in self.valid_fields:
                    warnings.append(f"⚠️ Неизвестное поле: {field}")
            
            # Формирование отчёта
            result = []
            
            if not issues and not warnings:
                result.append("✅ Manifest.json валиден")
            
            if issues:
                result.append("🚨 КРИТИЧЕСКИЕ ОШИБКИ:")
                result.extend(issues)
            
            if warnings:
                result.append("⚠️ ПРЕДУПРЕЖДЕНИЯ:")
                result.extend(warnings)
            
            is_valid = len(issues) == 0
            
            return ToolResult(
                success=True,
                data={
                    "valid": is_valid,
                    "issues": issues,
                    "warnings": warnings,
                    "report": "\n".join(result),
                    "manifest": manifest
                }
            )
            
        except Exception as e:
            logger.error(f"Ошибка ManifestValidatorTool: {e}")
            return ToolResult(success=False, error=str(e))
    
    def get_schema(self):
        """Схема для валидации manifest"""
        return {
            "type": "object",
            "properties": {
                "manifest_path": {
                    "type": "string",
                    "description": "Путь к файлу manifest.json"
                }
            },
            "required": ["manifest_path"]
        }
    
    def _is_valid_version(self, version: str) -> bool:
        """Проверка формата версии"""
        parts = version.split(".")
        if len(parts) < 2 or len(parts) > 4:
            return False
        
        for part in parts:
            if not part.isdigit():
                return False
        
        return True
    
    def _validate_permissions_v3(self, permissions: List[str], issues: List[str], warnings: List[str]):
        """Валидация permissions для Manifest V3"""
        deprecated_permissions = {
            "background": "Используйте service_worker в background",
            "tabs": "Используйте activeTab для большинства случаев"
        }
        
        for permission in permissions:
            if permission in deprecated_permissions:
                warnings.append(f"⚠️ {permission}: {deprecated_permissions[permission]}")


class HumanRequestTool(Tool):
    """Инструмент для запроса помощи у пользователя"""
    
    def __init__(self):
        super().__init__(
            name="human_request",
            description="Запрос помощи у пользователя когда агенту нужна помощь"
        )
    
    def execute(self, request_type: str, message: str, context: Dict[str, Any] = None, **kwargs):
        """
        Запросить помощь у пользователя
        
        Args:
            request_type: Тип запроса (auth, decision, config, approval)
            message: Сообщение для пользователя
            context: Дополнительный контекст
        """
        from tools import ToolResult
        
        try:
            context = context or {}
            
            # Форматируем запрос красиво
            request_emoji = {
                "auth": "🔑",
                "decision": "🤔", 
                "config": "⚙️",
                "approval": "✅",
                "help": "🆘"
            }
            
            emoji = request_emoji.get(request_type, "❓")
            
            formatted_request = f"""
{emoji} ТРЕБУЕТСЯ ПОМОЩЬ ПОЛЬЗОВАТЕЛЯ

Тип запроса: {request_type.upper()}
Сообщение: {message}

Контекст:
{json.dumps(context, indent=2, ensure_ascii=False)}

---
🤖 Агент ожидает ввода пользователя...
"""
            
            # В реальной системе здесь был бы механизм ожидания ответа от пользователя
            # Пока просто возвращаем форматированный запрос
            return ToolResult(
                success=True,
                data={
                    "request_type": request_type,
                    "message": message,
                    "context": context,
                    "formatted_request": formatted_request,
                    "awaiting_user_input": True
                }
            )
            
        except Exception as e:
            logger.error(f"Ошибка HumanRequestTool: {e}")
            return ToolResult(success=False, error=str(e))
    
    def get_schema(self):
        """Схема для запросов к пользователю"""
        return {
            "type": "object",
            "properties": {
                "request_type": {
                    "type": "string",
                    "enum": ["auth", "decision", "config", "approval", "help"],
                    "description": "Тип запроса к пользователю"
                },
                "message": {
                    "type": "string",
                    "description": "Сообщение для пользователя"
                },
                "context": {
                    "type": "object",
                    "description": "Дополнительный контекст (опционально)"
                }
            },
            "required": ["request_type", "message"]
        }


# Регистрация инструментов
BROWSER_TOOLS = [
    FileSystemTool(),
    ManifestValidatorTool(), 
    HumanRequestTool()
]

# Экспорт для удобного импорта
__all__ = [
    "FileSystemTool",
    "ManifestValidatorTool", 
    "HumanRequestTool",
    "BROWSER_TOOLS"
] 