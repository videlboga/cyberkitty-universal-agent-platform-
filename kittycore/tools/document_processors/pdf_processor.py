"""
Процессор PDF файлов для KittyCore 3.0
Обработка PDF документов с множественными fallback стратегиями
"""

import time
from typing import Dict, Any, List, Tuple, Optional

from ..document_common import DocumentFormat, DocumentMetadata, ExtractionResult
from .base_processor import DocumentProcessor


class PDFProcessor(DocumentProcessor):
    """Процессор для обработки PDF файлов"""
    
    def __init__(self):
        super().__init__()
        self.supported_formats = [DocumentFormat.PDF]
        self.available_libraries = self._check_libraries()
    
    def _check_libraries(self) -> Dict[str, bool]:
        """Проверка доступности библиотек для PDF"""
        libraries = {}
        
        # PyMuPDF (fitz)
        try:
            import fitz
            libraries['fitz'] = True
        except ImportError:
            libraries['fitz'] = False
        
        # pdfplumber
        try:
            import pdfplumber
            libraries['pdfplumber'] = True
        except ImportError:
            libraries['pdfplumber'] = False
        
        # PyPDF2
        try:
            import PyPDF2
            libraries['pypdf2'] = True
        except ImportError:
            libraries['pypdf2'] = False
        
        # pdfminer
        try:
            from pdfminer.high_level import extract_text
            libraries['pdfminer'] = True
        except ImportError:
            libraries['pdfminer'] = False
        
        return libraries
    
    async def process(self, file_data: bytes, metadata: DocumentMetadata) -> ExtractionResult:
        """Обработка PDF файла"""
        start_time = time.time()
        
        # Валидация
        is_valid, error_msg = self.validate_file(file_data, metadata)
        if not is_valid:
            return self.create_error_result(metadata, error_msg)
        
        # Пробуем различные библиотеки по приоритету
        extraction_methods = [
            ('fitz', self._extract_with_fitz),
            ('pdfplumber', self._extract_with_pdfplumber),
            ('pdfminer', self._extract_with_pdfminer),
            ('pypdf2', self._extract_with_pypdf2)
        ]
        
        last_error = None
        
        for method_name, method_func in extraction_methods:
            if not self.available_libraries.get(method_name, False):
                continue
            
            try:
                text, tables, images = await method_func(file_data)
                
                if text.strip():  # Успешное извлечение
                    processing_time = self.measure_processing_time(start_time)
                    self.update_metadata_after_processing(metadata, text, processing_time)
                    
                    return ExtractionResult(
                        text=text,
                        metadata=metadata,
                        tables=tables,
                        images=images,
                        success=True,
                        extraction_method=f"{self.name}_{method_name}",
                        processing_details={
                            'method': method_name,
                            'libraries_available': self.available_libraries,
                            'processing_time': processing_time,
                            'text_length': len(text),
                            'tables_count': len(tables),
                            'images_count': len(images)
                        }
                    )
                    
            except Exception as e:
                last_error = f"{method_name}: {str(e)}"
                continue
        
        # Если все методы не сработали
        error_msg = f"Не удалось извлечь текст из PDF. Последняя ошибка: {last_error}"
        return self.create_error_result(metadata, error_msg)
    
    async def _extract_with_fitz(self, file_data: bytes) -> Tuple[str, List[Dict], List[Dict]]:
        """Извлечение с помощью PyMuPDF (fitz)"""
        import fitz
        import io
        
        text_parts = []
        tables = []
        images = []
        
        doc = fitz.open(stream=file_data, filetype="pdf")
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            
            # Извлечение текста
            page_text = page.get_text()
            if page_text.strip():
                text_parts.append(f"--- Страница {page_num + 1} ---\n{page_text}")
            
            # Извлечение изображений (базовая информация)
            image_list = page.get_images()
            for img_index, img in enumerate(image_list):
                images.append({
                    'page': page_num + 1,
                    'index': img_index,
                    'xref': img[0],
                    'width': img[2] if len(img) > 2 else None,
                    'height': img[3] if len(img) > 3 else None
                })
        
        doc.close()
        return "\n\n".join(text_parts), tables, images
    
    async def _extract_with_pdfplumber(self, file_data: bytes) -> Tuple[str, List[Dict], List[Dict]]:
        """Извлечение с помощью pdfplumber"""
        import pdfplumber
        import io
        
        text_parts = []
        tables = []
        images = []
        
        with pdfplumber.open(io.BytesIO(file_data)) as pdf:
            for page_num, page in enumerate(pdf.pages):
                
                # Извлечение текста
                page_text = page.extract_text()
                if page_text and page_text.strip():
                    text_parts.append(f"--- Страница {page_num + 1} ---\n{page_text}")
                
                # Извлечение таблиц
                page_tables = page.extract_tables()
                for table_index, table in enumerate(page_tables):
                    if table:
                        tables.append({
                            'page': page_num + 1,
                            'index': table_index,
                            'data': table,
                            'rows': len(table),
                            'columns': len(table[0]) if table else 0
                        })
        
        return "\n\n".join(text_parts), tables, images
    
    async def _extract_with_pdfminer(self, file_data: bytes) -> Tuple[str, List[Dict], List[Dict]]:
        """Извлечение с помощью pdfminer"""
        from pdfminer.high_level import extract_text
        import io
        
        text = extract_text(io.BytesIO(file_data))
        return text, [], []
    
    async def _extract_with_pypdf2(self, file_data: bytes) -> Tuple[str, List[Dict], List[Dict]]:
        """Извлечение с помощью PyPDF2"""
        import PyPDF2
        import io
        
        text_parts = []
        
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_data))
        
        for page_num, page in enumerate(pdf_reader.pages):
            try:
                page_text = page.extract_text()
                if page_text and page_text.strip():
                    text_parts.append(f"--- Страница {page_num + 1} ---\n{page_text}")
            except Exception:
                continue  # Пропускаем проблемные страницы
        
        return "\n\n".join(text_parts), [], []


def create_pdf_processor() -> PDFProcessor:
    """Фабричная функция для создания процессора"""
    return PDFProcessor() 