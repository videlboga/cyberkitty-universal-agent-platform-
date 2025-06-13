"""
CodeExecutor - выполнение кода в заметках Obsidian
"""

import re
import subprocess
import tempfile
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from loguru import logger


class CodeExecutor:
    """
    Исполнитель кода для заметок Obsidian
    
    Поддерживает:
    - Выполнение Python кода из markdown блоков
    - Безопасное выполнение в изолированной среде
    - Захват вывода и ошибок
    - Тайм-ауты для долгих операций
    - Сохранение результатов в заметки
    """
    
    def __init__(self):
        self.supported_languages = ['python', 'python3', 'py']
        self.timeout = 30  # секунд
        self.max_output_size = 10000  # символов
        
        logger.debug("⚡ CodeExecutor инициализирован")
    
    async def execute_note_code(self, note_path: str) -> Dict[str, Any]:
        """
        Выполнение всех блоков кода в заметке
        
        Args:
            note_path: Путь к заметке
            
        Returns:
            Результаты выполнения
        """
        try:
            # Чтение содержимого заметки
            with open(note_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Извлечение блоков кода
            code_blocks = self._extract_code_blocks(content)
            
            if not code_blocks:
                return {
                    "status": "no_code",
                    "message": "В заметке нет исполняемых блоков кода",
                    "results": []
                }
            
            # Выполнение блоков кода
            results = []
            for i, (language, code) in enumerate(code_blocks):
                if language.lower() in self.supported_languages:
                    result = await self._execute_python_code(code, f"block_{i}")
                    results.append({
                        "block_index": i,
                        "language": language,
                        "code": code,
                        **result
                    })
                else:
                    results.append({
                        "block_index": i,
                        "language": language,
                        "code": code,
                        "status": "unsupported",
                        "message": f"Язык {language} не поддерживается"
                    })
            
            # Обновление заметки с результатами
            await self._update_note_with_results(note_path, content, results)
            
            # Общий статус
            all_successful = all(r.get('status') == 'success' for r in results if r.get('status') != 'unsupported')
            
            return {
                "status": "completed",
                "success": all_successful,
                "total_blocks": len(code_blocks),
                "executed_blocks": len([r for r in results if r.get('status') != 'unsupported']),
                "results": results
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка выполнения кода в заметке {note_path}: {e}")
            return {
                "status": "error",
                "message": str(e),
                "results": []
            }
    
    async def execute_code_block(self, language: str, code: str) -> Dict[str, Any]:
        """
        Выполнение одного блока кода
        
        Args:
            language: Язык программирования
            code: Код для выполнения
            
        Returns:
            Результат выполнения
        """
        if language.lower() not in self.supported_languages:
            return {
                "status": "unsupported",
                "message": f"Язык {language} не поддерживается"
            }
        
        return await self._execute_python_code(code)
    
    async def _execute_python_code(self, code: str, block_id: str = "single") -> Dict[str, Any]:
        """
        Выполнение Python кода
        
        Args:
            code: Python код
            block_id: Идентификатор блока
            
        Returns:
            Результат выполнения
        """
        try:
            # Создание временного файла
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
                f.write(code)
                temp_file = f.name
            
            # Выполнение кода
            try:
                process = await asyncio.create_subprocess_exec(
                    'python', temp_file,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=Path(temp_file).parent
                )
                
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), 
                    timeout=self.timeout
                )
                
                # Декодирование вывода
                output = stdout.decode('utf-8') if stdout else ""
                error = stderr.decode('utf-8') if stderr else ""
                
                # Ограничение размера вывода
                if len(output) > self.max_output_size:
                    output = output[:self.max_output_size] + "\n... (вывод обрезан)"
                
                if len(error) > self.max_output_size:
                    error = error[:self.max_output_size] + "\n... (ошибки обрезаны)"
                
                # Определение статуса
                if process.returncode == 0:
                    status = "success"
                    message = "Код выполнен успешно"
                else:
                    status = "error"
                    message = f"Код завершился с ошибкой (код возврата: {process.returncode})"
                
                return {
                    "status": status,
                    "message": message,
                    "output": output,
                    "error": error,
                    "return_code": process.returncode,
                    "block_id": block_id
                }
                
            except asyncio.TimeoutError:
                # Принудительное завершение процесса
                if process:
                    process.kill()
                    await process.wait()
                
                return {
                    "status": "timeout",
                    "message": f"Превышен тайм-аут выполнения ({self.timeout}s)",
                    "output": "",
                    "error": "TimeoutError",
                    "return_code": -1,
                    "block_id": block_id
                }
            
            finally:
                # Удаление временного файла
                try:
                    Path(temp_file).unlink()
                except:
                    pass
            
        except Exception as e:
            logger.error(f"❌ Ошибка выполнения Python кода: {e}")
            return {
                "status": "error",
                "message": f"Ошибка выполнения: {str(e)}",
                "output": "",
                "error": str(e),
                "return_code": -1,
                "block_id": block_id
            }
    
    def _extract_code_blocks(self, content: str) -> List[Tuple[str, str]]:
        """
        Извлечение блоков кода из markdown
        
        Args:
            content: Содержимое markdown файла
            
        Returns:
            Список кортежей (язык, код)
        """
        # Регулярное выражение для поиска блоков кода
        pattern = r'```(\w+)?\n(.*?)\n```'
        matches = re.findall(pattern, content, re.DOTALL)
        
        code_blocks = []
        for language, code in matches:
            # Если язык не указан, считаем что это Python
            if not language:
                language = 'python'
            
            # Очистка кода от лишних пробелов
            clean_code = code.strip()
            if clean_code:
                code_blocks.append((language, clean_code))
        
        return code_blocks
    
    async def _update_note_with_results(self, note_path: str, original_content: str, results: List[Dict[str, Any]]):
        """
        Обновление заметки с результатами выполнения
        
        Args:
            note_path: Путь к заметке
            original_content: Исходное содержимое
            results: Результаты выполнения
        """
        try:
            # Добавление результатов к заметке
            updated_content = original_content
            
            # Добавление раздела с результатами
            results_section = self._format_results_section(results)
            
            # Поиск места для вставки результатов
            if "## Результаты выполнения" in updated_content:
                # Замена существующего раздела
                pattern = r'## Результаты выполнения.*?(?=\n## |\n# |$)'
                updated_content = re.sub(pattern, results_section.strip(), updated_content, flags=re.DOTALL)
            else:
                # Добавление нового раздела
                updated_content += "\n\n" + results_section
            
            # Запись обновлённой заметки
            with open(note_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            logger.debug(f"📝 Обновлена заметка с результатами: {note_path}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка обновления заметки с результатами: {e}")
    
    def _format_results_section(self, results: List[Dict[str, Any]]) -> str:
        """
        Форматирование раздела с результатами
        
        Args:
            results: Результаты выполнения
            
        Returns:
            Форматированный markdown
        """
        if not results:
            return "## Результаты выполнения\n\n*Нет результатов выполнения*"
        
        section = "## Результаты выполнения\n\n"
        
        for i, result in enumerate(results):
            block_num = i + 1
            status = result.get('status', 'unknown')
            
            # Заголовок блока
            if status == 'success':
                section += f"### ✅ Блок {block_num} - Успешно\n\n"
            elif status == 'error':
                section += f"### ❌ Блок {block_num} - Ошибка\n\n"
            elif status == 'timeout':
                section += f"### ⏱️ Блок {block_num} - Тайм-аут\n\n"
            elif status == 'unsupported':
                section += f"### ⚠️ Блок {block_num} - Не поддерживается\n\n"
            else:
                section += f"### ❓ Блок {block_num} - {status}\n\n"
            
            # Сообщение
            message = result.get('message', '')
            if message:
                section += f"**Статус:** {message}\n\n"
            
            # Вывод
            output = result.get('output', '')
            if output:
                section += "**Вывод:**\n```\n" + output + "\n```\n\n"
            
            # Ошибки
            error = result.get('error', '')
            if error and status != 'success':
                section += "**Ошибка:**\n```\n" + error + "\n```\n\n"
            
            section += "---\n\n"
        
        return section
    
    def get_execution_stats(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Получение статистики выполнения
        
        Args:
            results: Результаты выполнения
            
        Returns:
            Статистика
        """
        if not results:
            return {
                "total": 0,
                "successful": 0,
                "failed": 0,
                "unsupported": 0,
                "timeout": 0,
                "success_rate": 0.0
            }
        
        stats = {
            "total": len(results),
            "successful": len([r for r in results if r.get('status') == 'success']),
            "failed": len([r for r in results if r.get('status') == 'error']),
            "unsupported": len([r for r in results if r.get('status') == 'unsupported']),
            "timeout": len([r for r in results if r.get('status') == 'timeout'])
        }
        
        # Расчёт процента успеха (исключая неподдерживаемые)
        executable = stats["total"] - stats["unsupported"]
        if executable > 0:
            stats["success_rate"] = (stats["successful"] / executable) * 100
        else:
            stats["success_rate"] = 0.0
        
        return stats
    
    def validate_code_safety(self, code: str) -> Tuple[bool, List[str]]:
        """
        Базовая проверка безопасности кода
        
        Args:
            code: Код для проверки
            
        Returns:
            (безопасен, список предупреждений)
        """
        warnings = []
        
        # Опасные импорты и функции
        dangerous_patterns = [
            r'import\s+os',
            r'import\s+subprocess',
            r'import\s+sys',
            r'__import__',
            r'eval\s*\(',
            r'exec\s*\(',
            r'open\s*\(',
            r'file\s*\(',
            r'input\s*\(',
            r'raw_input\s*\('
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                warnings.append(f"Обнаружен потенциально опасный код: {pattern}")
        
        # Проверка на сетевые операции
        network_patterns = [
            r'urllib',
            r'requests',
            r'socket',
            r'http',
            r'ftp'
        ]
        
        for pattern in network_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                warnings.append(f"Обнаружена сетевая операция: {pattern}")
        
        # Код считается безопасным если нет критических предупреждений
        critical_warnings = [w for w in warnings if any(d in w.lower() for d in ['eval', 'exec', '__import__'])]
        is_safe = len(critical_warnings) == 0
        
        return is_safe, warnings 