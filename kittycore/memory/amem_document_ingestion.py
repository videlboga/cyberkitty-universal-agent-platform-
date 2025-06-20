"""
📚 A-MEM Document Ingestion - Расширение A-MEM для RAG функционала

Вместо создания отдельного VectorSearchTool, расширяем A-MEM 
для работы с внешними документами и файлами.

Принцип: "Один мозг для всего - агентная память + документы" 🧠📚
"""

import asyncio
import logging
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import hashlib

try:
    import PyPDF2
    import docx
    from bs4 import BeautifulSoup
    DOC_DEPS_AVAILABLE = True
except ImportError:
    DOC_DEPS_AVAILABLE = False

from .amem_integration import KittyCoreMemorySystem, get_enhanced_memory_system

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Обработчик различных типов документов"""
    
    @staticmethod
    def extract_text_from_pdf(file_path: str) -> str:
        """Извлечение текста из PDF"""
        if not DOC_DEPS_AVAILABLE:
            raise ImportError("Установите зависимости: pip install PyPDF2 python-docx beautifulsoup4")
        
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                return text.strip()
        except Exception as e:
            logger.error(f"Ошибка чтения PDF {file_path}: {e}")
            return ""
    
    @staticmethod
    def extract_text_from_docx(file_path: str) -> str:
        """Извлечение текста из DOCX"""
        if not DOC_DEPS_AVAILABLE:
            raise ImportError("Установите зависимости: pip install python-docx")
        
        try:
            doc = docx.Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            logger.error(f"Ошибка чтения DOCX {file_path}: {e}")
            return ""
    
    @staticmethod
    def extract_text_from_html(file_path: str) -> str:
        """Извлечение текста из HTML"""
        if not DOC_DEPS_AVAILABLE:
            raise ImportError("Установите зависимости: pip install beautifulsoup4")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                soup = BeautifulSoup(file.read(), 'html.parser')
                # Удаляем скрипты и стили
                for script in soup(["script", "style"]):
                    script.decompose()
                return soup.get_text().strip()
        except Exception as e:
            logger.error(f"Ошибка чтения HTML {file_path}: {e}")
            return ""
    
    @staticmethod
    def extract_text_from_txt(file_path: str) -> str:
        """Извлечение текста из TXT"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read().strip()
        except Exception as e:
            logger.error(f"Ошибка чтения TXT {file_path}: {e}")
            return ""

class AMEMDocumentIngestion:
    """
    🧠📚 Расширение A-MEM для работы с документами
    
    Интегрирует внешние документы в агентную память для RAG функционала.
    Превосходит классический VectorSearchTool через A-MEM возможности.
    """
    
    def __init__(self, vault_path: str = "obsidian_vault"):
        self.memory_system = get_enhanced_memory_system(vault_path)
        self.document_processor = DocumentProcessor()
        self.vault_path = Path(vault_path)
        
        # Папка для хранения обработанных документов
        self.documents_folder = self.vault_path / "knowledge"
        self.documents_folder.mkdir(exist_ok=True)
        
        logger.info(f"📚 A-MEM Document Ingestion инициализирован: {vault_path}")
    
    async def ingest_file(self, file_path: str, 
                         category: str = "document",
                         metadata: Dict[str, Any] = None) -> str:
        """
        Загрузка файла в A-MEM память
        
        Args:
            file_path: Путь к файлу
            category: Категория документа  
            metadata: Дополнительные метаданные
        
        Returns:
            memory_id: ID созданной записи в памяти
        """
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                raise FileNotFoundError(f"Файл не найден: {file_path}")
            
            # Извлекаем текст в зависимости от типа файла
            text_content = await self._extract_text(file_path)
            
            if not text_content:
                raise ValueError(f"Не удалось извлечь текст из {file_path}")
            
            # Готовим метаданные
            file_metadata = {
                "source_file": str(file_path),
                "file_name": file_path.name,
                "file_size": file_path.stat().st_size,
                "file_extension": file_path.suffix,
                "file_hash": self._calculate_file_hash(file_path),
                "ingestion_date": datetime.now().isoformat(),
                "category": category,
                **(metadata or {})
            }
            
            # Сохраняем в A-MEM как память агента-документа
            memory_id = await self.memory_system.agent_remember(
                agent_id=f"document_{file_path.stem}",
                memory=text_content,
                context=file_metadata
            )
            
            # Сохраняем копию документа в knowledge base
            await self._save_to_knowledge_base(file_path, text_content, file_metadata)
            
            logger.info(f"📚 Документ загружен в A-MEM: {file_path.name} → {memory_id}")
            return memory_id
            
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки документа {file_path}: {e}")
            raise
    
    async def ingest_directory(self, 
                             directory_path: str,
                             file_patterns: List[str] = None,
                             recursive: bool = True) -> List[str]:
        """
        Массовая загрузка документов из папки
        
        Args:
            directory_path: Путь к папке
            file_patterns: Паттерны файлов (*.pdf, *.docx, etc.)
            recursive: Рекурсивный поиск
        
        Returns:
            List[memory_id]: ID созданных записей
        """
        try:
            directory_path = Path(directory_path)
            
            if not directory_path.exists():
                raise FileNotFoundError(f"Папка не найдена: {directory_path}")
            
            # Паттерны по умолчанию
            if file_patterns is None:
                file_patterns = ["*.pdf", "*.docx", "*.txt", "*.html", "*.md"]
            
            # Поиск файлов
            found_files = []
            for pattern in file_patterns:
                if recursive:
                    found_files.extend(directory_path.rglob(pattern))
                else:
                    found_files.extend(directory_path.glob(pattern))
            
            # Загрузка файлов
            memory_ids = []
            for file_path in found_files:
                try:
                    memory_id = await self.ingest_file(
                        str(file_path),
                        category="batch_upload",
                        metadata={"batch_source": str(directory_path)}
                    )
                    memory_ids.append(memory_id)
                except Exception as e:
                    logger.error(f"Ошибка загрузки {file_path}: {e}")
                    continue
            
            logger.info(f"📚 Массовая загрузка завершена: {len(memory_ids)}/{len(found_files)} файлов")
            return memory_ids
            
        except Exception as e:
            logger.error(f"❌ Ошибка массовой загрузки из {directory_path}: {e}")
            raise
    
    async def search_documents(self, 
                             query: str, 
                             category: str = None,
                             limit: int = 5) -> List[Dict[str, Any]]:
        """
        Семантический поиск по документам через A-MEM
        
        Args:
            query: Поисковый запрос
            category: Фильтр по категории
            limit: Количество результатов
        
        Returns:
            List[Dict]: Результаты поиска с метаданными
        """
        try:
            # Поиск через A-MEM коллективную память
            results = await self.memory_system.collective_search(
                query=query,
                team_id="documents"  # все документы как одна команда
            )
            
            # Фильтрация по категории если указана
            if category:
                filtered_results = []
                for result in results:
                    context = result.get('context', {})
                    if context.get('category') == category:
                        filtered_results.append(result)
                results = filtered_results
            
            # Ограничиваем количество результатов
            return results[:limit]
            
        except Exception as e:
            logger.error(f"❌ Ошибка поиска документов: {e}")
            return []
    
    async def get_document_stats(self) -> Dict[str, Any]:
        """Статистика загруженных документов"""
        try:
            # Поиск всех документов
            all_docs = await self.search_documents("", limit=1000)
            
            # Анализ статистики
            stats = {
                "total_documents": len(all_docs),
                "categories": {},
                "file_types": {},
                "total_size": 0,
                "latest_ingestion": None
            }
            
            for doc in all_docs:
                context = doc.get('context', {})
                
                # Категории
                category = context.get('category', 'unknown')
                stats["categories"][category] = stats["categories"].get(category, 0) + 1
                
                # Типы файлов
                file_ext = context.get('file_extension', 'unknown')
                stats["file_types"][file_ext] = stats["file_types"].get(file_ext, 0) + 1
                
                # Размер
                file_size = context.get('file_size', 0)
                stats["total_size"] += file_size
                
                # Последняя загрузка
                ingestion_date = context.get('ingestion_date')
                if ingestion_date:
                    if not stats["latest_ingestion"] or ingestion_date > stats["latest_ingestion"]:
                        stats["latest_ingestion"] = ingestion_date
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения статистики: {e}")
            return {"error": str(e)}
    
    async def _extract_text(self, file_path: Path) -> str:
        """Извлечение текста из файла по расширению"""
        extension = file_path.suffix.lower()
        
        if extension == '.pdf':
            return self.document_processor.extract_text_from_pdf(str(file_path))
        elif extension == '.docx':
            return self.document_processor.extract_text_from_docx(str(file_path))
        elif extension in ['.html', '.htm']:
            return self.document_processor.extract_text_from_html(str(file_path))
        elif extension in ['.txt', '.md']:
            return self.document_processor.extract_text_from_txt(str(file_path))
        else:
            # Пробуем как текстовый файл
            return self.document_processor.extract_text_from_txt(str(file_path))
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Вычисление хеша файла для дедупликации"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    async def _save_to_knowledge_base(self, 
                                    file_path: Path, 
                                    text_content: str,
                                    metadata: Dict[str, Any]):
        """Сохранение документа в knowledge base vault"""
        try:
            # Создаём markdown файл в knowledge папке
            output_path = self.documents_folder / f"{file_path.stem}.md"
            
            markdown_content = f"""# {file_path.name}

## Метаданные
- **Источник**: {metadata.get('source_file', 'unknown')}
- **Размер**: {metadata.get('file_size', 0)} байт
- **Тип**: {metadata.get('file_extension', 'unknown')}
- **Загружено**: {metadata.get('ingestion_date', 'unknown')}
- **Хеш**: {metadata.get('file_hash', 'unknown')}

## Содержимое

{text_content}

---
*Обработано A-MEM Document Ingestion*
"""
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            logger.info(f"💾 Документ сохранён в knowledge base: {output_path}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения в knowledge base: {e}")


# === ФАБРИЧНАЯ ФУНКЦИЯ ===

def get_amem_document_ingestion(vault_path: str = "obsidian_vault") -> AMEMDocumentIngestion:
    """Получение системы загрузки документов в A-MEM"""
    return AMEMDocumentIngestion(vault_path)