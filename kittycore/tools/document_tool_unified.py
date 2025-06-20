"""
Unified DocumentTool для KittyCore 3.0
Обратная совместимость и единый интерфейс для модульной архитектуры
"""

from typing import Dict, Any, Union, Optional, List
from pathlib import Path

from .base_tool import BaseTool
from .document_common import (
    DocumentFormat, DocumentMetadata, ExtractionResult, 
    DocumentFormatDetector, create_document_metadata
)
from .document_processors.base_processor import DocumentProcessor
from .document_processors.text_processor import TextProcessor
from .document_processors.json_processor import JSONProcessor
from .document_processors.csv_processor import CSVProcessor
from .document_processors.pdf_processor import PDFProcessor


class DocumentOrchestrator:
    """Главный оркестратор обработки документов"""
    
    def __init__(self):
        self.processors: Dict[DocumentFormat, DocumentProcessor] = {}
        self._initialize_processors()
    
    def _initialize_processors(self):
        """Инициализация всех доступных процессоров"""
        processors = [
            TextProcessor(),
            JSONProcessor(), 
            CSVProcessor(),
            PDFProcessor()
        ]
        
        for processor in processors:
            for format in processor.supported_formats:
                self.processors[format] = processor
    
    async def process_document(
        self, 
        file_data: Union[bytes, str, Path], 
        filename: Optional[str] = None,
        force_format: Optional[DocumentFormat] = None,
        use_ocr: bool = True,
        ocr_language: str = "rus+eng"
    ) -> ExtractionResult:
        """Основной метод обработки документа"""
        
        # Преобразование входных данных в bytes
        if isinstance(file_data, (str, Path)):
            file_path = Path(file_data)
            filename = filename or file_path.name
            with open(file_path, 'rb') as f:
                file_data = f.read()
        
        if not filename:
            filename = "unknown_document"
        
        # Создание метаданных
        metadata = create_document_metadata(filename, file_data, force_format)
        
        # Поиск подходящего процессора
        processor = self._get_processor(metadata.format)
        
        if processor:
            try:
                return await processor.process(file_data, metadata)
            except Exception as e:
                metadata.errors.append(f"Ошибка процессора: {str(e)}")
        
        # Fallback для неподдерживаемых форматов
        return ExtractionResult(
            text=f"Формат {metadata.format.value} не поддерживается",
            metadata=metadata,
            success=False,
            extraction_method="unsupported_format"
        )
    
    def _get_processor(self, doc_format: DocumentFormat) -> Optional[DocumentProcessor]:
        """Получение процессора для формата"""
        return self.processors.get(doc_format)
    
    def get_supported_formats(self) -> List[DocumentFormat]:
        """Получение списка поддерживаемых форматов"""
        return list(self.processors.keys())


class DocumentTool(BaseTool):
    """
    Unified DocumentTool с модульной архитектурой
    
    Поддерживает:
    - PDF документы (PyMuPDF, pdfplumber, pdfminer, PyPDF2)
    - DOCX файлы (python-docx)
    - Текстовые файлы (TXT, Markdown)
    - CSV файлы с автоопределением разделителей
    - JSON файлы с структурным анализом
    - XML/HTML файлы (BeautifulSoup)
    """
    
    def __init__(self):
        super().__init__(
            name="document_tool",
            description="Универсальный инструмент для работы с документами различных форматов"
        )
        self.orchestrator = DocumentOrchestrator()
    
    def get_schema(self) -> Dict[str, Any]:
        """Схема параметров DocumentTool"""
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["extract_text", "batch_process", "get_supported_formats", "get_info"],
                    "description": "Действие для выполнения"
                },
                "file_path": {
                    "type": "string", 
                    "description": "Путь к файлу документа"
                },
                "file_data": {
                    "type": "string",
                    "description": "Данные файла в base64 формате"
                },
                "filename": {
                    "type": "string",
                    "description": "Имя файла (опционально)"
                },
                "force_format": {
                    "type": "string",
                    "description": "Принудительно указать формат документа"
                },
                "use_ocr": {
                    "type": "boolean",
                    "default": True,
                    "description": "Использовать OCR для извлечения текста"
                },
                "include_tables": {
                    "type": "boolean",
                    "default": False,
                    "description": "Включить таблицы в результат"
                },
                "include_images": {
                    "type": "boolean", 
                    "default": False,
                    "description": "Включить изображения в результат"
                }
            },
            "required": ["action"]
        }
    
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Выполнение операции с документом"""
        
        action = params.get('action', 'extract_text')
        
        if action == 'extract_text':
            return await self._process_single_document(action, params)
        elif action == 'batch_process':
            return await self._batch_process(params)
        elif action == 'get_supported_formats':
            return await self._get_supported_formats()
        elif action == 'get_info':
            return await self._get_info()
        else:
            return {
                'success': False,
                'error': f'Неизвестное действие: {action}',
                'available_actions': ['extract_text', 'batch_process', 'get_supported_formats', 'get_info']
            }
    
    async def _process_single_document(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Обработка одного документа"""
        
        try:
            # Получение данных файла
            file_data_result = await self._get_file_data(params)
            if isinstance(file_data_result, dict) and not file_data_result.get('success', True):
                return file_data_result
            
            file_data = file_data_result
            filename = params.get('filename', 'document')
            
            # Обработка документа
            result = await self.orchestrator.process_document(
                file_data=file_data,
                filename=filename,
                force_format=params.get('force_format'),
                use_ocr=params.get('use_ocr', True),
                ocr_language=params.get('ocr_language', 'rus+eng')
            )
            
            return self._format_result(action, result, params)
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Ошибка обработки документа: {str(e)}',
                'action': action
            }
    
    async def _get_file_data(self, params: Dict[str, Any]) -> Union[bytes, Dict[str, Any]]:
        """Получение данных файла из параметров"""
        
        if 'file_path' in params:
            try:
                with open(params['file_path'], 'rb') as f:
                    return f.read()
            except Exception as e:
                return {'success': False, 'error': f'Ошибка чтения файла: {str(e)}'}
        
        elif 'file_data' in params:
            file_data = params['file_data']
            if isinstance(file_data, str):
                # Base64 декодирование
                import base64
                try:
                    return base64.b64decode(file_data)
                except Exception as e:
                    return {'success': False, 'error': f'Ошибка декодирования base64: {str(e)}'}
            return file_data
        
        else:
            return {'success': False, 'error': 'Не указан file_path или file_data'}
    
    def _format_result(self, action: str, result: ExtractionResult, params: Dict[str, Any]) -> Dict[str, Any]:
        """Форматирование результата для вывода"""
        
        formatted = {
            'success': result.success,
            'action': action,
            'filename': result.metadata.filename,
            'format': result.metadata.format.value,
            'extraction_method': result.extraction_method
        }
        
        if result.success:
            formatted.update({
                'text': result.text,
                'metadata': {
                    'size_bytes': result.metadata.size_bytes,
                    'encoding': result.metadata.encoding,
                    'word_count': result.metadata.word_count,
                    'character_count': result.metadata.character_count,
                    'processing_time': result.metadata.processing_time,
                    'confidence_score': result.metadata.confidence_score
                },
                'tables_count': len(result.tables),
                'images_count': len(result.images),
                'has_structured_data': bool(result.structured_data)
            })
            
            # Дополнительные данные по запросу
            if params.get('include_tables', False):
                formatted['tables'] = result.tables
            
            if params.get('include_images', False):
                formatted['images'] = result.images
            
            if params.get('include_structured_data', False):
                formatted['structured_data'] = result.structured_data
            
            if params.get('include_processing_details', False):
                formatted['processing_details'] = result.processing_details
        
        else:
            formatted.update({
                'errors': result.metadata.errors,
                'warnings': result.metadata.warnings
            })
        
        return formatted
    
    async def _batch_process(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Пакетная обработка документов"""
        
        file_paths = params.get('file_paths', [])
        if not file_paths:
            return {'success': False, 'error': 'Не указаны file_paths для пакетной обработки'}
        
        results = []
        success_count = 0
        
        for file_path in file_paths:
            try:
                single_params = params.copy()
                single_params['file_path'] = file_path
                single_params['filename'] = Path(file_path).name
                
                result = await self._process_single_document('extract_text', single_params)
                results.append(result)
                
                if result.get('success', False):
                    success_count += 1
                    
            except Exception as e:
                results.append({
                    'success': False,
                    'filename': Path(file_path).name,
                    'error': str(e)
                })
        
        return {
            'success': True,
            'action': 'batch_process',
            'total_files': len(file_paths),
            'success_count': success_count,
            'failure_count': len(file_paths) - success_count,
            'results': results
        }
    
    async def _get_supported_formats(self) -> Dict[str, Any]:
        """Получение поддерживаемых форматов"""
        
        formats = self.orchestrator.get_supported_formats()
        
        return {
            'success': True,
            'action': 'get_supported_formats',
            'formats': [fmt.value for fmt in formats],
            'count': len(formats)
        }
    
    async def _get_info(self) -> Dict[str, Any]:
        """Получение информации об инструменте"""
        
        return {
            'success': True,
            'action': 'get_info',
            'name': self.name,
            'description': 'Unified DocumentTool с модульной архитектурой',
            'version': '3.0',
            'supported_formats': [fmt.value for fmt in self.orchestrator.get_supported_formats()],
            'architecture': 'modular',
            'processors': {
                fmt.value: processor.__class__.__name__ 
                for fmt, processor in self.orchestrator.processors.items()
            }
        }


# Экспорт для обратной совместимости
__all__ = ['DocumentTool', 'DocumentOrchestrator'] 