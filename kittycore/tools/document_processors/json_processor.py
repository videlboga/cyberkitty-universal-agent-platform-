"""
Процессор JSON файлов для KittyCore 3.0
Обработка JSON данных и преобразование в читаемый текст
"""

import json
import time
from typing import Dict, Any, Union, List

from ..document_common import DocumentFormat, DocumentMetadata, ExtractionResult, DocumentUtils
from .base_processor import DocumentProcessor


class JSONProcessor(DocumentProcessor):
    """Процессор для обработки JSON файлов"""
    
    def __init__(self):
        super().__init__()
        self.supported_formats = [DocumentFormat.JSON]
    
    async def process(self, file_data: bytes, metadata: DocumentMetadata) -> ExtractionResult:
        """Обработка JSON файла"""
        start_time = time.time()
        
        # Валидация
        is_valid, error_msg = self.validate_file(file_data, metadata)
        if not is_valid:
            return self.create_error_result(metadata, error_msg)
        
        try:
            # Определение кодировки
            encoding = metadata.encoding or DocumentUtils.detect_encoding(file_data)
            metadata.encoding = encoding
            
            # Декодирование JSON
            json_text = file_data.decode(encoding, errors='replace')
            json_data = json.loads(json_text)
            
            # Преобразование в читаемый текст
            readable_text = self._json_to_readable_text(json_data)
            
            # Анализ структуры JSON
            structure_info = self._analyze_json_structure(json_data)
            
            # Обновление метаданных
            processing_time = self.measure_processing_time(start_time)
            self.update_metadata_after_processing(metadata, readable_text, processing_time)
            
            return ExtractionResult(
                text=readable_text,
                metadata=metadata,
                structured_data={
                    'json_data': json_data,
                    'structure_info': structure_info
                },
                success=True,
                extraction_method=f"{self.name}_encoding_{encoding}",
                processing_details={
                    'encoding': encoding,
                    'json_size': len(json_text),
                    'readable_size': len(readable_text),
                    'processing_time': processing_time,
                    'structure': structure_info
                }
            )
            
        except json.JSONDecodeError as e:
            return self.create_error_result(metadata, f"Невалидный JSON: {str(e)}")
        except UnicodeDecodeError as e:
            return self.create_error_result(metadata, f"Ошибка декодирования: {str(e)}")
        except Exception as e:
            return self.create_error_result(metadata, f"Ошибка обработки JSON: {str(e)}")
    
    def _json_to_readable_text(self, data: Union[Dict, List, Any], level: int = 0) -> str:
        """Преобразование JSON в читаемый текст"""
        indent = "  " * level
        
        if isinstance(data, dict):
            if not data:
                return "Пустой объект"
            
            lines = []
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    lines.append(f"{indent}{key}:")
                    lines.append(self._json_to_readable_text(value, level + 1))
                else:
                    lines.append(f"{indent}{key}: {self._format_value(value)}")
            return "\n".join(lines)
            
        elif isinstance(data, list):
            if not data:
                return f"{indent}Пустой массив"
            
            lines = []
            for i, item in enumerate(data):
                if isinstance(item, (dict, list)):
                    lines.append(f"{indent}Элемент {i + 1}:")
                    lines.append(self._json_to_readable_text(item, level + 1))
                else:
                    lines.append(f"{indent}Элемент {i + 1}: {self._format_value(item)}")
            return "\n".join(lines)
            
        else:
            return f"{indent}{self._format_value(data)}"
    
    def _format_value(self, value: Any) -> str:
        """Форматирование значения для читаемого вывода"""
        if value is None:
            return "null"
        elif isinstance(value, bool):
            return "да" if value else "нет"
        elif isinstance(value, str):
            # Ограничиваем длинные строки
            if len(value) > 100:
                return f'"{value[:97]}..."'
            return f'"{value}"'
        elif isinstance(value, (int, float)):
            return str(value)
        else:
            return str(value)
    
    def _analyze_json_structure(self, data: Union[Dict, List, Any]) -> Dict[str, Any]:
        """Анализ структуры JSON данных"""
        def count_structure(obj, counts=None):
            if counts is None:
                counts = {
                    'objects': 0,
                    'arrays': 0,
                    'strings': 0,
                    'numbers': 0,
                    'booleans': 0,
                    'nulls': 0,
                    'max_depth': 0,
                    'total_keys': 0
                }
            
            if isinstance(obj, dict):
                counts['objects'] += 1
                counts['total_keys'] += len(obj)
                for value in obj.values():
                    count_structure(value, counts)
                    
            elif isinstance(obj, list):
                counts['arrays'] += 1
                for item in obj:
                    count_structure(item, counts)
                    
            elif isinstance(obj, str):
                counts['strings'] += 1
            elif isinstance(obj, (int, float)):
                counts['numbers'] += 1
            elif isinstance(obj, bool):
                counts['booleans'] += 1
            elif obj is None:
                counts['nulls'] += 1
                
            return counts
        
        structure = count_structure(data)
        
        # Определение типа корневого элемента
        if isinstance(data, dict):
            root_type = "object"
        elif isinstance(data, list):
            root_type = "array"
        else:
            root_type = "primitive"
        
        structure['root_type'] = root_type
        structure['total_elements'] = sum(v for k, v in structure.items() 
                                        if k not in ['max_depth', 'root_type', 'total_keys'])
        
        return structure


def create_json_processor() -> JSONProcessor:
    """Фабричная функция для создания процессора"""
    return JSONProcessor() 