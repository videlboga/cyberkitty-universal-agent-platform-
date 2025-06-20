"""
Тесты для MediaTool - инструмента для работы с медиафайлами
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

from kittycore.tools.media_tool import MediaTool

# Проверяем доступность PIL для создания тестовых изображений
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


@pytest.fixture
def media_tool():
    """Фикстура для MediaTool"""
    return MediaTool()


@pytest.fixture
def test_image():
    """Фикстура с тестовым изображением"""
    if not PIL_AVAILABLE:
        pytest.skip("PIL не установлен")
    
    # Создаем простое тестовое изображение 100x100 пикселей
    img = Image.new('RGB', (100, 100), color='red')
    
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
        img.save(f.name, 'PNG')
        yield f.name
    
    # Очистка
    Path(f.name).unlink(missing_ok=True)


@pytest.fixture
def test_text_file():
    """Фикстура с тестовым текстовым файлом"""
    content = "Это тестовый файл.\nВторая строка.\nТретья строка с текстом."
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write(content)
        f.flush()  # Принудительная запись на диск
        yield f.name
    
    # Очистка
    Path(f.name).unlink(missing_ok=True)


class TestMediaTool:
    """Тесты для MediaTool"""
    
    def test_initialization(self, media_tool):
        """Тест инициализации"""
        assert media_tool.name == "media_tool"
        assert "медиафайлов" in media_tool.description
        assert len(media_tool.image_formats) > 0
        assert len(media_tool.video_formats) > 0
        assert len(media_tool.audio_formats) > 0
        assert len(media_tool.document_formats) > 0
        assert isinstance(media_tool.capabilities, dict)
    
    def test_get_schema(self, media_tool):
        """Тест получения схемы"""
        schema = media_tool.get_schema()
        
        assert schema['type'] == 'object'
        assert 'action' in schema['properties']
        assert 'required' in schema
        assert 'action' in schema['required']
        
        # Проверяем что все действия присутствуют в enum
        actions = schema['properties']['action']['enum']
        expected_actions = [
            'analyze_file', 'resize_image', 'convert_image',
            'extract_metadata', 'get_info', 'list_formats'
        ]
        for action in expected_actions:
            assert action in actions
    
    def test_list_formats(self, media_tool):
        """Тест получения списка форматов"""
        result = media_tool.execute(action="list_formats")
        
        assert result.success is True
        assert 'image_formats' in result.data
        assert 'video_formats' in result.data
        assert 'audio_formats' in result.data
        assert 'document_formats' in result.data
        
        # Проверяем что форматы не пустые
        assert len(result.data['image_formats']) > 0
        assert '.jpg' in result.data['image_formats']
        assert '.png' in result.data['image_formats']
    
    def test_get_info(self, media_tool):
        """Тест получения информации о возможностях"""
        result = media_tool.execute(action="get_info")
        
        assert result.success is True
        assert 'capabilities' in result.data
        assert 'image_formats' in result.data
        assert 'video_formats' in result.data
        
        capabilities = result.data['capabilities']
        assert 'image_processing' in capabilities
        assert 'video_processing' in capabilities
        assert 'advanced_image' in capabilities
    
    def test_analyze_nonexistent_file(self, media_tool):
        """Тест анализа несуществующего файла"""
        result = media_tool.execute(action="analyze_file", file_path="nonexistent.jpg")
        
        assert result.success is False
        assert 'не найден' in result.error
    
    def test_analyze_text_file(self, media_tool, test_text_file):
        """Тест анализа текстового файла"""
        result = media_tool.execute(action="analyze_file", file_path=test_text_file)
        
        assert result.success is True
        assert 'file_info' in result.data
        assert 'specific_info' in result.data
        
        file_info = result.data['file_info']
        assert file_info['type'] == 'document'
        assert file_info['extension'] == '.txt'
        assert file_info['size_bytes'] > 0
        
        # Проверяем анализ текстового файла
        specific_info = result.data['specific_info']
        if 'lines' in specific_info:  # Если удалось проанализировать
            assert specific_info['lines'] == 3
            assert specific_info['words'] > 0
            assert specific_info['characters'] > 0
    
    @pytest.mark.skipif(not PIL_AVAILABLE, reason="PIL не установлен")
    def test_analyze_image_file(self, media_tool, test_image):
        """Тест анализа изображения"""
        result = media_tool.execute(action="analyze_file", file_path=test_image)
        
        assert result.success is True
        assert 'file_info' in result.data
        assert 'specific_info' in result.data
        
        file_info = result.data['file_info']
        assert file_info['type'] == 'image'
        assert file_info['extension'] == '.png'
        
        # Проверяем анализ изображения
        specific_info = result.data['specific_info']
        if 'width' in specific_info:  # Если PIL доступен
            assert specific_info['width'] == 100
            assert specific_info['height'] == 100
            assert specific_info['format'] == 'PNG'
            assert specific_info['megapixels'] == 0.01  # 100x100 = 10,000 = 0.01 MP
    
    @pytest.mark.skipif(not PIL_AVAILABLE, reason="PIL не установлен")
    def test_resize_image(self, media_tool, test_image):
        """Тест изменения размера изображения"""
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as output_file:
            result = media_tool.execute(
                action="resize_image",
                file_path=test_image,
                output_path=output_file.name,
                width=50,
                height=50,
                quality=90
            )
            
            assert result.success is True
            assert 'original_size' in result.data
            assert 'new_size' in result.data
            assert result.data['original_size'] == (100, 100)
            assert result.data['new_size'] == (50, 50)
            assert result.data['quality'] == 90
            
            # Проверяем что файл создан
            assert Path(output_file.name).exists()
            
            # Очистка
            Path(output_file.name).unlink(missing_ok=True)
    
    @pytest.mark.skipif(not PIL_AVAILABLE, reason="PIL не установлен")
    def test_resize_image_proportional(self, media_tool, test_image):
        """Тест пропорционального изменения размера"""
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as output_file:
            result = media_tool.execute(
                action="resize_image",
                file_path=test_image,
                output_path=output_file.name,
                width=50  # Только ширина - высота должна масштабироваться
            )
            
            assert result.success is True
            assert result.data['new_size'] == (50, 50)  # Пропорциональное изменение
            
            # Очистка
            Path(output_file.name).unlink(missing_ok=True)
    
    @pytest.mark.skipif(not PIL_AVAILABLE, reason="PIL не установлен")
    def test_convert_image(self, media_tool, test_image):
        """Тест конвертации изображения"""
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as output_file:
            result = media_tool.execute(
                action="convert_image",
                file_path=test_image,
                output_path=output_file.name,
                format="JPEG",
                quality=85
            )
            
            assert result.success is True
            assert 'original_format' in result.data
            assert 'new_format' in result.data
            assert result.data['original_format'] == 'PNG'
            assert result.data['new_format'] == 'JPEG'
            assert result.data['quality'] == 85
            
            # Проверяем что файл создан
            assert Path(output_file.name).exists()
            
            # Очистка
            Path(output_file.name).unlink(missing_ok=True)
    
    def test_resize_without_dimensions(self, media_tool, test_image):
        """Тест изменения размера без указания размеров"""
        result = media_tool.execute(
            action="resize_image",
            file_path=test_image,
            output_path="output.png"
        )
        
        assert result.success is False
        assert 'необходимо указать' in result.error.lower()
    
    def test_resize_nonexistent_file(self, media_tool):
        """Тест изменения размера несуществующего файла"""
        result = media_tool.execute(
            action="resize_image",
            file_path="nonexistent.jpg",
            output_path="output.jpg",
            width=100
        )
        
        assert result.success is False
        assert 'не найден' in result.error
    
    def test_invalid_action(self, media_tool):
        """Тест вызова несуществующего действия"""
        result = media_tool.execute(action="unknown_action")
        
        assert result.success is False
        assert 'Неизвестное действие' in result.error
        assert 'available_actions' in result.data
    
    def test_format_file_size(self, media_tool):
        """Тест форматирования размера файла"""
        assert media_tool._format_file_size(512) == "512.0 B"
        assert media_tool._format_file_size(1024) == "1.0 KB"
        assert media_tool._format_file_size(1024 * 1024) == "1.0 MB"
        assert media_tool._format_file_size(1024 * 1024 * 1024) == "1.0 GB"
    
    def test_detect_file_type(self, media_tool):
        """Тест определения типа файла"""
        assert media_tool._detect_file_type(Path("test.jpg")) == "image"
        assert media_tool._detect_file_type(Path("test.mp4")) == "video"
        assert media_tool._detect_file_type(Path("test.mp3")) == "audio"
        assert media_tool._detect_file_type(Path("test.pdf")) == "document"
        assert media_tool._detect_file_type(Path("test.unknown")) == "unknown"
    
    def test_without_pil_resize(self, media_tool, test_text_file):
        """Тест изменения размера без PIL"""
        with patch('kittycore.tools.media_tool.PIL_AVAILABLE', False):
            result = media_tool.execute(
                action="resize_image",
                file_path=test_text_file,
                output_path="output.jpg",
                width=100
            )
            
            assert result.success is False
            assert 'PIL/Pillow не установлен' in result.error 