"""
Общие компоненты для работы с документами в KittyCore 3.0
Структуры данных, утилиты и детекторы форматов
"""

import os
import io
import json
import tempfile
import mimetypes
import hashlib
import zipfile
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


class DocumentFormat(Enum):
    """Поддерживаемые форматы документов"""
    PDF = "pdf"
    DOCX = "docx"
    DOC = "doc"
    TXT = "txt"
    RTF = "rtf"
    ODT = "odt"
    CSV = "csv"
    JSON = "json"
    XML = "xml"
    HTML = "html"
    MARKDOWN = "md"
    EXCEL = "xlsx"
    POWERPOINT = "pptx"
    IMAGE = "image"  # jpg, png, etc.
    UNKNOWN = "unknown"


class ProcessingStrategy(Enum):
    """Стратегии обработки документов"""
    AUTO = "auto"           # Автоматический выбор лучшей стратегии
    LIGHTWEIGHT = "lightweight"  # Быстрая обработка, базовые библиотеки
    ADVANCED = "advanced"   # Продвинутая обработка, сложные алгоритмы
    CLOUD = "cloud"        # Облачные сервисы (AWS, Google, Azure)
    HYBRID = "hybrid"      # Комбинация локальных и облачных методов


@dataclass
class DocumentMetadata:
    """Метаданные документа"""
    filename: str
    format: DocumentFormat
    size_bytes: int
    mime_type: str
    encoding: Optional[str] = None
    page_count: Optional[int] = None
    word_count: Optional[int] = None
    character_count: Optional[int] = None
    created_date: Optional[datetime] = None
    modified_date: Optional[datetime] = None
    author: Optional[str] = None
    title: Optional[str] = None
    subject: Optional[str] = None
    checksum: Optional[str] = None
    processing_time: Optional[float] = None
    confidence_score: Optional[float] = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass 
class ExtractionResult:
    """Результат извлечения данных из документа"""
    text: str
    metadata: DocumentMetadata
    tables: List[Dict[str, Any]] = field(default_factory=list)
    images: List[Dict[str, Any]] = field(default_factory=list)
    structured_data: Dict[str, Any] = field(default_factory=dict)
    raw_data: Optional[bytes] = None
    success: bool = True
    extraction_method: str = "unknown"
    processing_details: Dict[str, Any] = field(default_factory=dict)


class DocumentUtils:
    """Утилиты для работы с документами"""
    
    @staticmethod
    def calculate_checksum(data: bytes) -> str:
        """Вычисление MD5 хеша данных"""
        return hashlib.md5(data).hexdigest()
    
    @staticmethod
    def detect_encoding(data: bytes) -> str:
        """Определение кодировки текстовых данных"""
        try:
            import chardet
            result = chardet.detect(data)
            return result.get('encoding', 'utf-8') or 'utf-8'
        except ImportError:
            # Fallback без chardet
            encodings = ['utf-8', 'windows-1251', 'cp1252', 'latin-1']
            for encoding in encodings:
                try:
                    data.decode(encoding)
                    return encoding
                except UnicodeDecodeError:
                    continue
            return 'utf-8'
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Очистка имени файла от опасных символов"""
        dangerous_chars = '<>:"/\\|?*'
        for char in dangerous_chars:
            filename = filename.replace(char, '_')
        return filename
    
    @staticmethod
    def create_temp_file(data: bytes, suffix: str = None) -> str:
        """Создание временного файла с данными"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(data)
            return tmp.name
    
    @staticmethod
    def cleanup_temp_file(filepath: str) -> None:
        """Удаление временного файла"""
        try:
            if os.path.exists(filepath):
                os.unlink(filepath)
        except Exception:
            pass  # Игнорируем ошибки удаления
    
    @staticmethod
    def validate_file_size(data: bytes, max_size_mb: int = 100) -> Tuple[bool, str]:
        """Валидация размера файла"""
        size_mb = len(data) / (1024 * 1024)
        if size_mb > max_size_mb:
            return False, f"Файл слишком большой: {size_mb:.1f}MB > {max_size_mb}MB"
        return True, "OK"
    
    @staticmethod
    def count_words(text: str) -> int:
        """Подсчёт слов в тексте"""
        if not text:
            return 0
        return len(text.split())
    
    @staticmethod
    def extract_metadata_from_content(text: str) -> Dict[str, Any]:
        """Извлечение метаданных из содержимого"""
        return {
            'word_count': DocumentUtils.count_words(text),
            'character_count': len(text),
            'line_count': len(text.splitlines()),
            'paragraph_count': len([p for p in text.split('\n\n') if p.strip()])
        }


class DocumentFormatDetector:
    """Умный детектор форматов документов"""
    
    # Magic bytes для определения формата по содержимому
    MAGIC_BYTES = {
        b'%PDF': DocumentFormat.PDF,
        b'PK\x03\x04': DocumentFormat.DOCX,  # ZIP-based formats
        b'\xd0\xcf\x11\xe0': DocumentFormat.DOC,  # MS Office old format
        b'{\rtf': DocumentFormat.RTF,
        b'PK': DocumentFormat.ODT,  # OpenDocument также ZIP-based
        b'\x89PNG': DocumentFormat.IMAGE,
        b'\xff\xd8\xff': DocumentFormat.IMAGE,  # JPEG
        b'GIF8': DocumentFormat.IMAGE,
        b'<html': DocumentFormat.HTML,
        b'<!DOCTYPE': DocumentFormat.HTML,
        b'<?xml': DocumentFormat.XML,
    }
    
    # MIME типы для дополнительной проверки
    MIME_MAPPING = {
        'application/pdf': DocumentFormat.PDF,
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': DocumentFormat.DOCX,
        'application/msword': DocumentFormat.DOC,
        'application/rtf': DocumentFormat.RTF,
        'application/vnd.oasis.opendocument.text': DocumentFormat.ODT,
        'text/plain': DocumentFormat.TXT,
        'text/csv': DocumentFormat.CSV,
        'application/json': DocumentFormat.JSON,
        'application/xml': DocumentFormat.XML,
        'text/xml': DocumentFormat.XML,
        'text/html': DocumentFormat.HTML,
        'text/markdown': DocumentFormat.MARKDOWN,
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': DocumentFormat.EXCEL,
        'application/vnd.openxmlformats-officedocument.presentationml.presentation': DocumentFormat.POWERPOINT,
        'image/jpeg': DocumentFormat.IMAGE,
        'image/png': DocumentFormat.IMAGE,
        'image/gif': DocumentFormat.IMAGE,
        'image/bmp': DocumentFormat.IMAGE,
        'image/tiff': DocumentFormat.IMAGE,
    }
    
    @classmethod
    def detect_format(cls, file_data: bytes, filename: str = None, mime_type: str = None) -> DocumentFormat:
        """Определяет формат документа по содержимому, имени файла и MIME типу"""
        
        # 1. Проверка по magic bytes (наиболее надёжно)
        for magic, doc_format in cls.MAGIC_BYTES.items():
            if file_data.startswith(magic):
                # Дополнительная проверка для ZIP-based форматов
                if magic == b'PK\x03\x04' and filename:
                    return cls._detect_zip_based_format(file_data, filename)
                return doc_format
        
        # 2. Проверка по MIME типу
        if mime_type and mime_type in cls.MIME_MAPPING:
            return cls.MIME_MAPPING[mime_type]
        
        # 3. Проверка по расширению файла
        if filename:
            extension = Path(filename).suffix.lower().lstrip('.')
            for doc_format in DocumentFormat:
                if doc_format.value == extension:
                    return doc_format
        
        # 4. Эвристическая проверка содержимого
        return cls._heuristic_detection(file_data)
    
    @classmethod
    def _detect_zip_based_format(cls, file_data: bytes, filename: str) -> DocumentFormat:
        """Определяет конкретный формат для ZIP-based файлов"""
        try:
            with io.BytesIO(file_data) as bio:
                with zipfile.ZipFile(bio, 'r') as zf:
                    filenames = zf.namelist()
                    
                    # Проверка на DOCX
                    if 'word/document.xml' in filenames:
                        return DocumentFormat.DOCX
                    
                    # Проверка на XLSX
                    if 'xl/workbook.xml' in filenames:
                        return DocumentFormat.EXCEL
                    
                    # Проверка на PPTX
                    if 'ppt/presentation.xml' in filenames:
                        return DocumentFormat.POWERPOINT
                    
                    # Проверка на ODT
                    if 'content.xml' in filenames and 'META-INF/manifest.xml' in filenames:
                        return DocumentFormat.ODT
                        
        except Exception:
            pass
        
        # Fallback по расширению
        extension = Path(filename).suffix.lower().lstrip('.')
        format_map = {
            'docx': DocumentFormat.DOCX,
            'xlsx': DocumentFormat.EXCEL,
            'pptx': DocumentFormat.POWERPOINT,
            'odt': DocumentFormat.ODT
        }
        return format_map.get(extension, DocumentFormat.UNKNOWN)
    
    @classmethod
    def _heuristic_detection(cls, file_data: bytes) -> DocumentFormat:
        """Эвристическое определение формата по содержимому"""
        try:
            # Попытка декодировать как текст
            text_sample = file_data[:1024].decode('utf-8', errors='ignore').lower()
            
            # Проверка на JSON
            if text_sample.strip().startswith(('{', '[')):
                try:
                    json.loads(file_data.decode('utf-8'))
                    return DocumentFormat.JSON
                except:
                    pass
            
            # Проверка на HTML
            if any(tag in text_sample for tag in ['<html', '<body', '<div', '<p>', '<!doctype']):
                return DocumentFormat.HTML
            
            # Проверка на XML
            if text_sample.strip().startswith('<?xml') or '<' in text_sample and '>' in text_sample:
                return DocumentFormat.XML
            
            # Проверка на CSV (примитивно)
            if ',' in text_sample and '\n' in text_sample:
                lines = text_sample.split('\n')[:5]
                if all(',' in line for line in lines if line.strip()):
                    return DocumentFormat.CSV
            
            # По умолчанию считаем текстом
            return DocumentFormat.TXT
            
        except Exception:
            return DocumentFormat.UNKNOWN


def create_document_metadata(
    filename: str,
    file_data: bytes,
    doc_format: DocumentFormat = None,
    mime_type: str = None
) -> DocumentMetadata:
    """Фабричная функция для создания метаданных документа"""
    
    if doc_format is None:
        doc_format = DocumentFormatDetector.detect_format(file_data, filename, mime_type)
    
    if mime_type is None:
        mime_type, _ = mimetypes.guess_type(filename)
        mime_type = mime_type or 'application/octet-stream'
    
    return DocumentMetadata(
        filename=filename,
        format=doc_format,
        size_bytes=len(file_data),
        mime_type=mime_type,
        checksum=DocumentUtils.calculate_checksum(file_data)
    ) 