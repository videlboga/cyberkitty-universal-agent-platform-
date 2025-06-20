"""
MediaTool для KittyCore 3.0 - Инструмент для работы с медиафайлами

Возможности:
- Обработка изображений (PIL/Pillow)
- Анализ медиафайлов
- Конвертация форматов
- Извлечение метаданных
- Изменение размеров и качества
"""

import os
import json
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import logging

try:
    from PIL import Image, ImageOps, ExifTags
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False

from .base_tool import Tool
from .unified_tool_result import ToolResult

logger = logging.getLogger(__name__)


class MediaTool(Tool):
    """
    Инструмент для работы с медиафайлами
    
    Основные возможности:
    - Обработка изображений (изменение размера, конвертация, фильтры)
    - Анализ метаданных медиафайлов
    - Конвертация между форматами
    - Извлечение информации о файлах
    """
    
    def __init__(self):
        super().__init__(
            name="media_tool",
            description="Инструмент для обработки медиафайлов: изображения, видео, аудио, документы"
        )
        
        # Поддерживаемые форматы
        self.image_formats = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp']
        self.video_formats = ['.mp4', '.avi', '.mov', '.mkv', '.webm']
        self.audio_formats = ['.mp3', '.wav', '.flac', '.ogg', '.aac']
        self.document_formats = ['.pdf', '.doc', '.docx', '.txt']
        
        # Проверка доступности библиотек
        self.capabilities = {
            'image_processing': PIL_AVAILABLE,
            'video_processing': OPENCV_AVAILABLE,
            'advanced_image': PIL_AVAILABLE and OPENCV_AVAILABLE
        }
        
        logger.info(f"MediaTool инициализирован. Возможности: {self.capabilities}")
    
    def get_schema(self) -> Dict[str, Any]:
        """JSON Schema для валидации параметров"""
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "description": "Действие для выполнения",
                    "enum": [
                        "analyze_file", "resize_image", "convert_image",
                        "extract_metadata", "get_info", "list_formats"
                    ]
                },
                "file_path": {
                    "type": "string",
                    "description": "Путь к медиафайлу"
                },
                "output_path": {
                    "type": "string",
                    "description": "Путь для сохранения результата"
                },
                "width": {
                    "type": "integer",
                    "description": "Ширина для изменения размера",
                    "minimum": 1
                },
                "height": {
                    "type": "integer",
                    "description": "Высота для изменения размера",
                    "minimum": 1
                },
                "quality": {
                    "type": "integer",
                    "description": "Качество сжатия (1-100)",
                    "minimum": 1,
                    "maximum": 100
                },
                "format": {
                    "type": "string",
                    "description": "Формат для конвертации",
                    "enum": ["JPEG", "PNG", "WEBP", "BMP", "TIFF"]
                }
            },
            "required": ["action"]
        }
    
    def execute(self, action: str, **kwargs) -> ToolResult:
        """Выполнение действий с медиафайлами"""
        try:
            if action == "analyze_file":
                return self._analyze_file(**kwargs)
            elif action == "resize_image":
                return self._resize_image(**kwargs)
            elif action == "convert_image":
                return self._convert_image(**kwargs)
            elif action == "extract_metadata":
                return self._extract_metadata(**kwargs)
            elif action == "get_info":
                return self._get_info()
            elif action == "list_formats":
                return self._list_formats()
            else:
                return ToolResult(
                    success=False,
                    error=f'Неизвестное действие: {action}',
                    data={
                        'available_actions': [
                            'analyze_file', 'resize_image', 'convert_image',
                            'extract_metadata', 'get_info', 'list_formats'
                        ]
                    }
                )
                
        except Exception as e:
            logger.error(f"Ошибка в MediaTool.execute: {e}")
            return ToolResult(success=False, error=str(e))
    
    def _analyze_file(self, file_path: str) -> ToolResult:
        """Анализ медиафайла"""
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                return ToolResult(
                    success=False,
                    error=f'Файл не найден: {file_path}'
                )
            
            # Базовая информация о файле
            file_stat = file_path.stat()
            file_info = {
                'name': file_path.name,
                'size_bytes': file_stat.st_size,
                'size_human': self._format_file_size(file_stat.st_size),
                'extension': file_path.suffix.lower(),
                'modified_time': file_stat.st_mtime
            }
            
            # Определение типа файла
            file_type = self._detect_file_type(file_path)
            file_info['type'] = file_type
            
            # Специфический анализ по типу файла
            specific_info = {}
            
            if file_type == 'image' and PIL_AVAILABLE:
                specific_info = self._analyze_image(file_path)
            elif file_type == 'video' and OPENCV_AVAILABLE:
                specific_info = self._analyze_video(file_path)
            elif file_type == 'audio':
                specific_info = self._analyze_audio(file_path)
            elif file_type == 'document':
                specific_info = self._analyze_document(file_path)
            
            result_data = {
                'file_info': file_info,
                'specific_info': specific_info,
                'capabilities_used': {
                    'PIL': PIL_AVAILABLE,
                    'OpenCV': OPENCV_AVAILABLE
                }
            }
            
            logger.info(f"Проанализирован файл: {file_path.name} ({file_type})")
            
            return ToolResult(
                success=True,
                data=result_data
            )
            
        except Exception as e:
            return ToolResult(success=False, error=f'Ошибка анализа файла: {str(e)}')
    
    def _resize_image(self, file_path: str, output_path: str, 
                     width: Optional[int] = None, height: Optional[int] = None,
                     quality: int = 95) -> ToolResult:
        """Изменение размера изображения"""
        try:
            if not PIL_AVAILABLE:
                return ToolResult(
                    success=False,
                    error='PIL/Pillow не установлен. Установите: pip install Pillow'
                )
            
            file_path = Path(file_path)
            output_path = Path(output_path)
            
            if not file_path.exists():
                return ToolResult(
                    success=False,
                    error=f'Файл не найден: {file_path}'
                )
            
            # Создание директории для выходного файла
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Открытие и обработка изображения
            with Image.open(file_path) as img:
                original_size = img.size
                
                # Определение нового размера
                if width and height:
                    new_size = (width, height)
                elif width:
                    # Пропорциональное изменение по ширине
                    ratio = width / original_size[0]
                    new_size = (width, int(original_size[1] * ratio))
                elif height:
                    # Пропорциональное изменение по высоте
                    ratio = height / original_size[1]
                    new_size = (int(original_size[0] * ratio), height)
                else:
                    return ToolResult(
                        success=False,
                        error='Необходимо указать width и/или height'
                    )
                
                # Изменение размера с высоким качеством
                resized_img = img.resize(new_size, Image.Resampling.LANCZOS)
                
                # Сохранение с указанным качеством
                save_kwargs = {'quality': quality, 'optimize': True}
                if resized_img.mode in ('RGBA', 'LA', 'P'):
                    # Конвертируем в RGB для JPEG
                    if output_path.suffix.lower() in ['.jpg', '.jpeg']:
                        resized_img = resized_img.convert('RGB')
                
                resized_img.save(output_path, **save_kwargs)
            
            # Информация о результате
            output_stat = output_path.stat()
            result_data = {
                'original_size': original_size,
                'new_size': new_size,
                'original_file_size': file_path.stat().st_size,
                'new_file_size': output_stat.st_size,
                'compression_ratio': round(output_stat.st_size / file_path.stat().st_size, 2),
                'output_path': str(output_path),
                'quality': quality
            }
            
            logger.info(f"Изображение изменено: {original_size} -> {new_size}")
            
            return ToolResult(
                success=True,
                data=result_data
            )
            
        except Exception as e:
            return ToolResult(success=False, error=f'Ошибка изменения размера: {str(e)}')
    
    def _convert_image(self, file_path: str, output_path: str,
                      format: str = "JPEG", quality: int = 95) -> ToolResult:
        """Конвертация изображения в другой формат"""
        try:
            if not PIL_AVAILABLE:
                return ToolResult(
                    success=False,
                    error='PIL/Pillow не установлен. Установите: pip install Pillow'
                )
            
            file_path = Path(file_path)
            output_path = Path(output_path)
            
            if not file_path.exists():
                return ToolResult(
                    success=False,
                    error=f'Файл не найден: {file_path}'
                )
            
            # Создание директории для выходного файла
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Открытие и конвертация изображения
            with Image.open(file_path) as img:
                original_format = img.format
                original_mode = img.mode
                
                # Подготовка изображения для конвертации
                converted_img = img
                
                # Обработка альфа-канала для JPEG
                if format == "JPEG" and img.mode in ('RGBA', 'LA', 'P'):
                    # Создаем белый фон для прозрачных изображений
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    converted_img = background
                
                # Сохранение в новом формате
                save_kwargs = {}
                if format in ['JPEG', 'WEBP']:
                    save_kwargs.update({'quality': quality, 'optimize': True})
                elif format == 'PNG':
                    save_kwargs.update({'optimize': True})
                
                converted_img.save(output_path, format=format, **save_kwargs)
            
            # Информация о результате
            result_data = {
                'original_format': original_format,
                'new_format': format,
                'original_mode': original_mode,
                'new_mode': converted_img.mode,
                'original_size': img.size,
                'original_file_size': file_path.stat().st_size,
                'new_file_size': output_path.stat().st_size,
                'output_path': str(output_path),
                'quality': quality
            }
            
            logger.info(f"Изображение конвертировано: {original_format} -> {format}")
            
            return ToolResult(
                success=True,
                data=result_data
            )
            
        except Exception as e:
            return ToolResult(success=False, error=f'Ошибка конвертации: {str(e)}')

    def _extract_metadata(self, file_path: str) -> ToolResult:
        """Извлечение метаданных из медиафайла"""
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                return ToolResult(
                    success=False,
                    error=f'Файл не найден: {file_path}'
                )
            
            # Извлечение метаданных с использованием PIL
            with Image.open(file_path) as img:
                metadata = {
                    'format': img.format,
                    'mode': img.mode,
                    'size': img.size,
                    'width': img.width,
                    'height': img.height,
                    'exif': img.getexif(),
                    'exif_tags': ExifTags.TAGS.get(img.getexif().get(0x010e), 'Неизвестно'),
                    'description': img.info.get('description', 'Неизвестно'),
                    'creation_time': img.info.get('creation_time', 'Неизвестно'),
                    'modified_time': img.info.get('modified_time', 'Неизвестно')
                }
            
            logger.info(f"Метаданные извлечены: {file_path.name}")
            
            return ToolResult(
                success=True,
                data=metadata
            )
            
        except Exception as e:
            return ToolResult(success=False, error=f'Ошибка извлечения метаданных: {str(e)}')

    def _get_info(self) -> ToolResult:
        """Получение информации о поддерживаемых форматах"""
        try:
            info = {
                'image_formats': self.image_formats,
                'video_formats': self.video_formats,
                'audio_formats': self.audio_formats,
                'document_formats': self.document_formats,
                'capabilities': self.capabilities
            }
            
            logger.info("Информация о поддерживаемых форматах получена")
            
            return ToolResult(
                success=True,
                data=info
            )
            
        except Exception as e:
            return ToolResult(success=False, error=f'Ошибка получения информации: {str(e)}')

    def _list_formats(self) -> ToolResult:
        """Список поддерживаемых форматов"""
        try:
            formats = {
                'image_formats': self.image_formats,
                'video_formats': self.video_formats,
                'audio_formats': self.audio_formats,
                'document_formats': self.document_formats
            }
            
            logger.info("Список поддерживаемых форматов получен")
            
            return ToolResult(
                success=True,
                data=formats
            )
            
        except Exception as e:
            return ToolResult(success=False, error=f'Ошибка получения списка форматов: {str(e)}')
    
    def _detect_file_type(self, file_path: Path) -> str:
        """Определение типа файла по расширению"""
        extension = file_path.suffix.lower()
        
        if extension in self.image_formats:
            return 'image'
        elif extension in self.video_formats:
            return 'video'
        elif extension in self.audio_formats:
            return 'audio'
        elif extension in self.document_formats:
            return 'document'
        else:
            return 'unknown'
    
    def _format_file_size(self, size_bytes: int) -> str:
        """Форматирование размера файла в человекочитаемый вид"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"
    
    def _analyze_image(self, file_path: Path) -> Dict[str, Any]:
        """Анализ изображения с помощью PIL"""
        try:
            with Image.open(file_path) as img:
                # Базовая информация
                info = {
                    'format': img.format,
                    'mode': img.mode,
                    'size': img.size,
                    'width': img.width,
                    'height': img.height,
                    'has_transparency': img.mode in ('RGBA', 'LA') or 'transparency' in img.info,
                    'dpi': img.info.get('dpi', (72, 72)),
                    'color_count': len(img.getcolors() or []) if img.mode in ('P', 'L') else 'N/A'
                }
                
                # EXIF данные если доступны
                exif_data = {}
                try:
                    exif = img.getexif()
                    for tag_id, value in exif.items():
                        tag = ExifTags.TAGS.get(tag_id, tag_id)
                        exif_data[tag] = value
                    info['exif'] = exif_data
                except:
                    info['exif'] = {}
                
                # Размер в пикселях и соотношение сторон
                info['aspect_ratio'] = round(img.width / img.height, 2)
                info['total_pixels'] = img.width * img.height
                info['megapixels'] = round(info['total_pixels'] / 1_000_000, 2)
                
                return info
                
        except Exception as e:
            return {'error': str(e)}
    
    def _analyze_video(self, file_path: Path) -> Dict[str, Any]:
        """Анализ видеофайла с помощью OpenCV"""
        try:
            if not OPENCV_AVAILABLE:
                return {'error': 'OpenCV не установлен'}
            
            cap = cv2.VideoCapture(str(file_path))
            
            if not cap.isOpened():
                return {'error': 'Не удалось открыть видеофайл'}
            
            # Получение свойств видео
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            info = {
                'fps': fps,
                'frame_count': frame_count,
                'width': width,
                'height': height,
                'duration_seconds': round(frame_count / fps if fps > 0 else 0, 2),
                'aspect_ratio': round(width / height if height > 0 else 0, 2),
                'total_pixels_per_frame': width * height,
                'codec': int(cap.get(cv2.CAP_PROP_FOURCC))
            }
            
            cap.release()
            return info
            
        except Exception as e:
            return {'error': str(e)}
    
    def _analyze_audio(self, file_path: Path) -> Dict[str, Any]:
        """Базовый анализ аудиофайла"""
        try:
            # Пока без специальных библиотек - только базовая информация
            info = {
                'format': file_path.suffix.lower(),
                'size_bytes': file_path.stat().st_size,
                'note': 'Для детального анализа аудио требуются дополнительные библиотеки (pydub, librosa)'
            }
            return info
            
        except Exception as e:
            return {'error': str(e)}
    
    def _analyze_document(self, file_path: Path) -> Dict[str, Any]:
        """Базовый анализ документа"""
        try:
            info = {
                'format': file_path.suffix.lower(),
                'size_bytes': file_path.stat().st_size,
                'note': 'Для детального анализа документов требуются дополнительные библиотеки (PyPDF2, python-docx)'
            }
            
            # Для текстовых файлов можем посчитать строки
            if file_path.suffix.lower() == '.txt':
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        info.update({
                            'lines': len(content.splitlines()),
                            'characters': len(content),
                            'words': len(content.split()),
                            'encoding': 'utf-8'
                        })
                except:
                    info['encoding_error'] = 'Не удалось прочитать как UTF-8'
            
            return info
            
        except Exception as e:
            return {'error': str(e)} 