"""
Процессор текстовых файлов для KittyCore 3.0
Обработка TXT, Markdown и других простых текстовых форматов
"""

import time
from typing import Dict, Any

from ..document_common import DocumentFormat, DocumentMetadata, ExtractionResult, DocumentUtils
from .base_processor import DocumentProcessor


class TextProcessor(DocumentProcessor):
    """Процессор для обработки текстовых файлов"""
    
    def __init__(self):
        super().__init__()
        self.supported_formats = [
            DocumentFormat.TXT,
            DocumentFormat.MARKDOWN
        ]
    
    async def process(self, file_data: bytes, metadata: DocumentMetadata) -> ExtractionResult:
        """Обработка текстового файла"""
        start_time = time.time()
        
        # Валидация
        is_valid, error_msg = self.validate_file(file_data, metadata)
        if not is_valid:
            return self.create_error_result(metadata, error_msg)
        
        try:
            # Определение кодировки
            encoding = metadata.encoding or DocumentUtils.detect_encoding(file_data)
            metadata.encoding = encoding
            
            # Декодирование текста
            text = file_data.decode(encoding, errors='replace')
            
            # Очистка текста (удаление лишних пробелов и переносов)
            cleaned_text = self._clean_text(text)
            
            # Извлечение структурированных данных для Markdown
            structured_data = {}
            if metadata.format == DocumentFormat.MARKDOWN:
                structured_data = self._extract_markdown_structure(cleaned_text)
            
            # Обновление метаданных
            processing_time = self.measure_processing_time(start_time)
            self.update_metadata_after_processing(metadata, cleaned_text, processing_time)
            
            return ExtractionResult(
                text=cleaned_text,
                metadata=metadata,
                structured_data=structured_data,
                success=True,
                extraction_method=f"{self.name}_encoding_{encoding}",
                processing_details={
                    'encoding': encoding,
                    'original_size': len(file_data),
                    'text_size': len(cleaned_text),
                    'processing_time': processing_time
                }
            )
            
        except UnicodeDecodeError as e:
            return self.create_error_result(metadata, f"Ошибка декодирования: {str(e)}")
        except Exception as e:
            return self.create_error_result(metadata, f"Ошибка обработки текста: {str(e)}")
    
    def _clean_text(self, text: str) -> str:
        """Очистка текста от лишних символов"""
        # Нормализация переносов строк
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        
        # Удаление лишних пробелов в конце строк
        lines = [line.rstrip() for line in text.split('\n')]
        
        # Удаление множественных пустых строк (оставляем максимум 2)
        cleaned_lines = []
        empty_count = 0
        
        for line in lines:
            if line.strip() == '':
                empty_count += 1
                if empty_count <= 2:
                    cleaned_lines.append(line)
            else:
                empty_count = 0
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines).strip()
    
    def _extract_markdown_structure(self, text: str) -> Dict[str, Any]:
        """Извлечение структуры из Markdown файла"""
        structure = {
            'headings': [],
            'links': [],
            'images': [],
            'code_blocks': [],
            'lists': []
        }
        
        lines = text.split('\n')
        in_code_block = False
        current_list = []
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # Заголовки
            if stripped.startswith('#'):
                level = len(stripped) - len(stripped.lstrip('#'))
                title = stripped.lstrip('#').strip()
                structure['headings'].append({
                    'level': level,
                    'title': title,
                    'line': i + 1
                })
            
            # Код блоки
            if stripped.startswith('```'):
                in_code_block = not in_code_block
                if not in_code_block:
                    language = stripped[3:].strip()
                    structure['code_blocks'].append({
                        'language': language,
                        'line': i + 1
                    })
            
            if not in_code_block:
                # Ссылки [text](url)
                import re
                link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
                links = re.findall(link_pattern, line)
                for text, url in links:
                    structure['links'].append({
                        'text': text,
                        'url': url,
                        'line': i + 1
                    })
                
                # Изображения ![alt](url)
                img_pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
                images = re.findall(img_pattern, line)
                for alt, url in images:
                    structure['images'].append({
                        'alt': alt,
                        'url': url,
                        'line': i + 1
                    })
                
                # Списки
                if stripped.startswith(('- ', '* ', '+ ')) or re.match(r'^\d+\.\s', stripped):
                    current_list.append({
                        'text': stripped,
                        'line': i + 1
                    })
                elif current_list and stripped == '':
                    continue  # Пустая строка в списке
                elif current_list:
                    # Конец списка
                    structure['lists'].append(current_list)
                    current_list = []
        
        # Добавляем последний список если есть
        if current_list:
            structure['lists'].append(current_list)
        
        return structure


def create_text_processor() -> TextProcessor:
    """Фабричная функция для создания процессора"""
    return TextProcessor() 