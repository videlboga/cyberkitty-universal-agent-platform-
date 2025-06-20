"""
Базовый процессор документов для KittyCore 3.0
Абстрактный класс для всех обработчиков форматов документов
"""

import time
from typing import Tuple, List
from abc import ABC, abstractmethod

from ..document_common import DocumentFormat, DocumentMetadata, ExtractionResult


class DocumentProcessor(ABC):
    """Базовый класс для обработчиков документов"""
    
    def __init__(self):
        self.name = self.__class__.__name__
        self.supported_formats: List[DocumentFormat] = []
        
    def can_process(self, file_format: DocumentFormat) -> bool:
        """Проверяет, может ли процессор обработать данный формат"""
        return file_format in self.supported_formats
        
    @abstractmethod
    async def process(self, file_data: bytes, metadata: DocumentMetadata) -> ExtractionResult:
        """Асинхронная обработка документа"""
        raise NotImplementedError("Subclasses must implement process method")
        
    def validate_file(self, file_data: bytes, metadata: DocumentMetadata) -> Tuple[bool, str]:
        """Валидация файла перед обработкой"""
        if not file_data:
            return False, "Файл пустой"
        if metadata.size_bytes > 100 * 1024 * 1024:  # 100MB
            return False, "Файл слишком большой (>100MB)"
        if metadata.format not in self.supported_formats:
            return False, f"Формат {metadata.format.value} не поддерживается"
        return True, "OK"
    
    def create_error_result(self, metadata: DocumentMetadata, error_message: str) -> ExtractionResult:
        """Создание результата с ошибкой"""
        metadata.errors.append(error_message)
        return ExtractionResult(
            text="",
            metadata=metadata,
            success=False,
            extraction_method=self.name
        )
    
    def measure_processing_time(self, start_time: float) -> float:
        """Измерение времени обработки"""
        return time.time() - start_time
    
    def update_metadata_after_processing(self, metadata: DocumentMetadata, text: str, processing_time: float):
        """Обновление метаданных после обработки"""
        from ..document_common import DocumentUtils
        
        metadata.word_count = DocumentUtils.count_words(text)
        metadata.character_count = len(text)
        metadata.processing_time = processing_time
        
        if text and len(text) > 0:
            metadata.confidence_score = min(1.0, len(text) / 1000)  # Простая оценка
        else:
            metadata.confidence_score = 0.0 