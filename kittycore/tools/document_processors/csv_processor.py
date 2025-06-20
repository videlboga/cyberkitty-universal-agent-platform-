"""
Процессор CSV файлов для KittyCore 3.0
Обработка CSV данных с автоопределением разделителей и кодировок
"""

import csv
import io
import time
from typing import Dict, Any, List, Optional, Tuple

from ..document_common import DocumentFormat, DocumentMetadata, ExtractionResult, DocumentUtils
from .base_processor import DocumentProcessor


class CSVProcessor(DocumentProcessor):
    """Процессор для обработки CSV файлов"""
    
    def __init__(self):
        super().__init__()
        self.supported_formats = [DocumentFormat.CSV]
    
    async def process(self, file_data: bytes, metadata: DocumentMetadata) -> ExtractionResult:
        """Обработка CSV файла"""
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
            csv_text = file_data.decode(encoding, errors='replace')
            
            # Автоопределение разделителя
            delimiter = self._detect_delimiter(csv_text)
            
            # Парсинг CSV
            csv_data, headers = self._parse_csv(csv_text, delimiter)
            
            # Преобразование в читаемый текст
            readable_text = self._csv_to_readable_text(csv_data, headers)
            
            # Анализ структуры CSV
            structure_info = self._analyze_csv_structure(csv_data, headers)
            
            # Обновление метаданных
            processing_time = self.measure_processing_time(start_time)
            self.update_metadata_after_processing(metadata, readable_text, processing_time)
            
            return ExtractionResult(
                text=readable_text,
                metadata=metadata,
                tables=[{
                    'headers': headers,
                    'data': csv_data,
                    'rows': len(csv_data),
                    'columns': len(headers) if headers else 0
                }],
                structured_data={
                    'csv_data': csv_data,
                    'headers': headers,
                    'structure_info': structure_info,
                    'delimiter': delimiter
                },
                success=True,
                extraction_method=f"{self.name}_delimiter_{repr(delimiter)}",
                processing_details={
                    'encoding': encoding,
                    'delimiter': delimiter,
                    'rows': len(csv_data),
                    'columns': len(headers) if headers else 0,
                    'processing_time': processing_time
                }
            )
            
        except UnicodeDecodeError as e:
            return self.create_error_result(metadata, f"Ошибка декодирования: {str(e)}")
        except Exception as e:
            return self.create_error_result(metadata, f"Ошибка обработки CSV: {str(e)}")
    
    def _detect_delimiter(self, csv_text: str) -> str:
        """Автоопределение разделителя CSV"""
        # Анализируем первые несколько строк
        sample_lines = csv_text.split('\n')[:10]
        sample = '\n'.join(sample_lines)
        
        # Возможные разделители
        delimiters = [',', ';', '\t', '|', ':']
        
        # Используем встроенный Sniffer
        try:
            sniffer = csv.Sniffer()
            dialect = sniffer.sniff(sample, delimiters=delimiters)
            return dialect.delimiter
        except:
            pass
        
        # Fallback: подсчёт частоты разделителей
        delimiter_counts = {}
        for delimiter in delimiters:
            count = 0
            for line in sample_lines:
                if line.strip():
                    count += line.count(delimiter)
            delimiter_counts[delimiter] = count
        
        # Возвращаем самый частый разделитель
        if delimiter_counts:
            return max(delimiter_counts, key=delimiter_counts.get)
        
        return ','  # По умолчанию
    
    def _parse_csv(self, csv_text: str, delimiter: str) -> Tuple[List[List[str]], Optional[List[str]]]:
        """Парсинг CSV данных"""
        rows = []
        headers = None
        
        try:
            # Создаём StringIO для csv.reader
            csv_file = io.StringIO(csv_text)
            reader = csv.reader(csv_file, delimiter=delimiter)
            
            # Читаем все строки
            all_rows = list(reader)
            
            if not all_rows:
                return [], None
            
            # Определяем заголовки (если первая строка содержит больше текста, чем цифр)
            first_row = all_rows[0]
            if self._is_header_row(first_row):
                headers = first_row
                rows = all_rows[1:]
            else:
                rows = all_rows
                # Генерируем заголовки
                if rows:
                    headers = [f"Колонка_{i+1}" for i in range(len(rows[0]))]
            
            # Нормализуем строки (одинаковое количество колонок)
            if headers:
                max_cols = len(headers)
                normalized_rows = []
                for row in rows:
                    # Дополняем короткие строки пустыми значениями
                    while len(row) < max_cols:
                        row.append('')
                    # Обрезаем длинные строки
                    normalized_rows.append(row[:max_cols])
                rows = normalized_rows
            
            return rows, headers
            
        except Exception as e:
            # В случае ошибки возвращаем построчный разбор
            lines = csv_text.strip().split('\n')
            rows = [line.split(delimiter) for line in lines if line.strip()]
            
            if rows:
                headers = [f"Колонка_{i+1}" for i in range(len(rows[0]))]
            
            return rows, headers
    
    def _is_header_row(self, row: List[str]) -> bool:
        """Определяет, является ли строка заголовком"""
        if not row:
            return False
        
        # Считаем текстовые и числовые поля
        text_count = 0
        number_count = 0
        
        for cell in row:
            cell = cell.strip()
            if not cell:
                continue
                
            try:
                float(cell)
                number_count += 1
            except ValueError:
                text_count += 1
        
        # Если больше текста, вероятно заголовок
        return text_count > number_count
    
    def _csv_to_readable_text(self, csv_data: List[List[str]], headers: Optional[List[str]]) -> str:
        """Преобразование CSV в читаемый текст"""
        if not csv_data:
            return "Пустой CSV файл"
        
        lines = []
        
        # Заголовок
        if headers:
            lines.append("CSV данные:")
            lines.append(f"Колонки: {', '.join(headers)}")
            lines.append(f"Строк данных: {len(csv_data)}")
            lines.append("")
        
        # Показываем первые несколько строк
        display_rows = min(10, len(csv_data))
        
        for i, row in enumerate(csv_data[:display_rows]):
            if headers:
                line_parts = []
                for j, (header, value) in enumerate(zip(headers, row)):
                    if value.strip():
                        line_parts.append(f"{header}: {value}")
                
                if line_parts:
                    lines.append(f"Строка {i+1}: {', '.join(line_parts)}")
            else:
                if any(cell.strip() for cell in row):
                    lines.append(f"Строка {i+1}: {', '.join(row)}")
        
        # Если строк больше, добавляем информацию
        if len(csv_data) > display_rows:
            lines.append(f"... и ещё {len(csv_data) - display_rows} строк")
        
        return "\n".join(lines)
    
    def _analyze_csv_structure(self, csv_data: List[List[str]], headers: Optional[List[str]]) -> Dict[str, Any]:
        """Анализ структуры CSV данных"""
        if not csv_data:
            return {'rows': 0, 'columns': 0, 'empty': True}
        
        structure = {
            'rows': len(csv_data),
            'columns': len(headers) if headers else 0,
            'empty': False,
            'column_types': {},
            'data_quality': {}
        }
        
        if headers and csv_data:
            # Анализ типов данных по колонкам
            for col_idx, header in enumerate(headers):
                column_data = [row[col_idx] if col_idx < len(row) else '' for row in csv_data]
                
                # Подсчёт типов данных
                empty_count = 0
                number_count = 0
                date_count = 0
                text_count = 0
                
                for value in column_data:
                    value = value.strip()
                    if not value:
                        empty_count += 1
                        continue
                    
                    # Проверка на число
                    try:
                        float(value)
                        number_count += 1
                        continue
                    except ValueError:
                        pass
                    
                    # Проверка на дату (простая)
                    if self._looks_like_date(value):
                        date_count += 1
                        continue
                    
                    text_count += 1
                
                # Определение доминирующего типа
                total_values = len(column_data) - empty_count
                if total_values == 0:
                    column_type = 'empty'
                elif number_count > total_values * 0.8:
                    column_type = 'number'
                elif date_count > total_values * 0.8:
                    column_type = 'date'
                else:
                    column_type = 'text'
                
                structure['column_types'][header] = {
                    'type': column_type,
                    'empty_count': empty_count,
                    'total_count': len(column_data)
                }
        
        return structure
    
    def _looks_like_date(self, value: str) -> bool:
        """Простая проверка на дату"""
        import re
        # Простые паттерны дат
        date_patterns = [
            r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
            r'\d{2}\.\d{2}\.\d{4}',  # DD.MM.YYYY
            r'\d{2}/\d{2}/\d{4}',   # MM/DD/YYYY
        ]
        
        for pattern in date_patterns:
            if re.match(pattern, value):
                return True
        return False


def create_csv_processor() -> CSVProcessor:
    """Фабричная функция для создания процессора"""
    return CSVProcessor() 