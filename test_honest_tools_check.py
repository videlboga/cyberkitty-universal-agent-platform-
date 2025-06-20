#!/usr/bin/env python3
"""
🕵️ ЧЕСТНАЯ ПРОВЕРКА ВСЕХ ИНСТРУМЕНТОВ KITTYCORE 3.0

Цель: Выявить фиктивные результаты и мок-ответы
Принцип: "Если нет API ключей - должна быть ошибка, а не успех!"

Проверяем:
- Реальные API вызовы vs фиктивные успехи  
- Действительно ли инструменты выполняют работу
- Возвращают ли реальные данные или заглушки
"""

import asyncio
import time
import json
import tempfile
import os
from pathlib import Path
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Импорт всех инструментов
from kittycore.tools.enhanced_web_search_tool import EnhancedWebSearchTool
from kittycore.tools.media_tool import MediaTool
from kittycore.tools.network_tool import NetworkTool
from kittycore.tools.api_request_tool import ApiRequestTool
from kittycore.tools.super_system_tool import SuperSystemTool
from kittycore.tools.computer_use_tool import ComputerUseTool
from kittycore.tools.communication_tools import EmailTool
from kittycore.tools.code_execution_tools import CodeExecutionTool
from kittycore.tools.data_analysis_tool import DataAnalysisTool

class HonestToolsChecker:
    """Честная проверка инструментов на фиктивные результаты"""
    
    def __init__(self):
        self.results = {}
        self.fake_patterns = [
            "демо режим", "demo mode", "заглушка", "mock", "fake", "test data",
            "пример", "example", "sample", "placeholder", "dummy"
        ]
        
    def detect_fake_result(self, result_data: str, tool_name: str) -> tuple:
        """Обнаружение фиктивных результатов"""
        result_str = str(result_data).lower()
        fake_indicators = []
        
        # Поиск паттернов заглушек
        for pattern in self.fake_patterns:
            if pattern in result_str:
                fake_indicators.append(f"Найден паттерн '{pattern}'")
        
        # Специфические проверки по инструментам
        if tool_name == "media_tool":
            if "image_processing" in result_str and "PIL" not in result_str:
                fake_indicators.append("Обработка изображений без PIL")
                
        elif tool_name == "email_tool":
            if "отправлен" in result_str and len(result_str) < 100:
                fake_indicators.append("Слишком короткий ответ для реальной отправки")
                
        elif tool_name == "enhanced_web_search":
            if "результат" in result_str and "http" not in result_str:
                fake_indicators.append("Поиск без реальных URL")
        
        is_fake = len(fake_indicators) > 0
        return is_fake, fake_indicators
        
    def test_enhanced_web_search(self):
        """🌐 Честный тест веб-поиска"""
        print("🌐 ЧЕСТНЫЙ ТЕСТ enhanced_web_search")
        
        tool = EnhancedWebSearchTool()
        
        # Проверяем реальный поиск
        result = tool.execute(
            action="search",
            query="Python programming tutorial 2024",
            max_results=3
        )
        
        success = result.success
        data_size = len(str(result.data)) if result.data else 0
        is_fake, fake_indicators = self.detect_fake_result(result.data, "enhanced_web_search")
        
        # Дополнительные проверки
        real_indicators = []
        if result.data and isinstance(result.data, dict):
            if "results" in result.data:
                results = result.data["results"]
                if isinstance(results, list) and len(results) > 0:
                    for res in results[:2]:
                        if isinstance(res, dict) and "url" in res:
                            if res["url"].startswith("http"):
                                real_indicators.append("Найдены реальные URL")
                                break
        
        verdict = "❌ ФИКТИВНЫЙ" if is_fake else "✅ РЕАЛЬНЫЙ" if real_indicators else "⚠️ СОМНИТЕЛЬНЫЙ"
        
        print(f"   Результат: {verdict}")
        print(f"   Успех: {success}, Размер: {data_size} байт")
        if fake_indicators:
            print(f"   🚨 Индикаторы подделки: {fake_indicators}")
        if real_indicators:
            print(f"   ✅ Индикаторы реальности: {real_indicators}")
            
        return {"tool": "enhanced_web_search", "success": success, "fake": is_fake, "size": data_size}
    
    def test_media_tool(self):
        """🎨 Честный тест медиа-инструмента"""
        print("🎨 ЧЕСТНЫЙ ТЕСТ media_tool")
        
        tool = MediaTool()
        
        # Создаём тестовое изображение
        test_image = self._create_test_image()
        
        try:
            # Пробуем РЕАЛЬНО обработать изображение
            result = tool.execute(
                action="analyze_file",
                file_path=str(test_image)
            )
            
            success = result.success
            data_size = len(str(result.data)) if result.data else 0
            is_fake, fake_indicators = self.detect_fake_result(result.data, "media_tool")
            
            # Проверяем реальную обработку
            real_indicators = []
            if result.data and isinstance(result.data, dict):
                if "file_info" in result.data:
                    file_info = result.data["file_info"]
                    if isinstance(file_info, dict) and "size_bytes" in file_info:
                        actual_size = test_image.stat().st_size
                        reported_size = file_info.get("size_bytes", 0)
                        if actual_size == reported_size:
                            real_indicators.append("Реальный размер файла")
                            
                if "specific_info" in result.data:
                    specific = result.data["specific_info"]
                    if isinstance(specific, dict) and "dimensions" in specific:
                        real_indicators.append("Реальные размеры изображения")
            
        except Exception as e:
            success = False
            data_size = 0
            is_fake = False
            fake_indicators = [f"Исключение: {str(e)[:50]}"]
            real_indicators = []
        finally:
            # Очистка
            if test_image.exists():
                test_image.unlink()
        
        verdict = "❌ ФИКТИВНЫЙ" if is_fake else "✅ РЕАЛЬНЫЙ" if real_indicators else "⚠️ СОМНИТЕЛЬНЫЙ"
        
        print(f"   Результат: {verdict}")
        print(f"   Успех: {success}, Размер: {data_size} байт")
        if fake_indicators:
            print(f"   🚨 Индикаторы подделки: {fake_indicators}")
        if real_indicators:
            print(f"   ✅ Индикаторы реальности: {real_indicators}")
            
        return {"tool": "media_tool", "success": success, "fake": is_fake, "size": data_size}
    
    def test_email_tool(self):
        """📧 Честный тест email инструмента"""
        print("📧 ЧЕСТНЫЙ ТЕСТ email_tool")
        
        tool = EmailTool()
        
        # Пробуем отправить email БЕЗ настроек SMTP
        result = tool.execute(
            action="send_email",
            to="test@example.com",
            subject="Test",
            body="Test message"
        )
        
        success = result.success
        data_size = len(str(result.data)) if result.data else 0
        is_fake, fake_indicators = self.detect_fake_result(result.data, "email_tool")
        
        # Критическая проверка: без SMTP настроек НЕ ДОЛЖНО быть успеха!
        if success and not os.getenv("SMTP_SERVER"):
            is_fake = True
            fake_indicators.append("Успех без SMTP настроек - подделка!")
        
        verdict = "❌ ФИКТИВНЫЙ" if is_fake else "✅ РЕАЛЬНЫЙ"
        
        print(f"   Результат: {verdict}")
        print(f"   Успех: {success}, Размер: {data_size} байт")
        if fake_indicators:
            print(f"   🚨 Индикаторы подделки: {fake_indicators}")
            
        return {"tool": "email_tool", "success": success, "fake": is_fake, "size": data_size}
    
    def test_network_tool(self):
        """🌐 Честный тест сетевого инструмента"""  
        print("🌐 ЧЕСТНЫЙ ТЕСТ network_tool")
        
        tool = NetworkTool()
        
        # Реальный ping к Google
        result = tool.execute(
            action="ping_host",
            host="google.com",
            count=1
        )
        
        success = result.success
        data_size = len(str(result.data)) if result.data else 0
        is_fake, fake_indicators = self.detect_fake_result(result.data, "network_tool")
        
        # Проверяем реальный ping
        real_indicators = []
        if result.data:
            data_str = str(result.data).lower()
            if any(indicator in data_str for indicator in ["ms", "time=", "bytes=", "ping", "ttl="]):
                real_indicators.append("Реальные ping метрики")
                
        verdict = "❌ ФИКТИВНЫЙ" if is_fake else "✅ РЕАЛЬНЫЙ" if real_indicators else "⚠️ СОМНИТЕЛЬНЫЙ"
        
        print(f"   Результат: {verdict}")
        print(f"   Успех: {success}, Размер: {data_size} байт")
        if fake_indicators:
            print(f"   🚨 Индикаторы подделки: {fake_indicators}")
        if real_indicators:
            print(f"   ✅ Индикаторы реальности: {real_indicators}")
            
        return {"tool": "network_tool", "success": success, "fake": is_fake, "size": data_size}
    
    def test_computer_use_tool(self):
        """💻 Честный тест GUI автоматизации"""
        print("💻 ЧЕСТНЫЙ ТЕСТ computer_use_tool")
        
        tool = ComputerUseTool()
        
        # Пробуем сделать скриншот (должно работать на Linux)
        result = tool.execute(action="screenshot")
        
        success = result.success  
        data_size = len(str(result.data)) if result.data else 0
        is_fake, fake_indicators = self.detect_fake_result(result.data, "computer_use_tool")
        
        # Проверяем реальный скриншот
        real_indicators = []
        if result.data and isinstance(result.data, dict):
            if "screenshot_path" in result.data or "image_data" in result.data:
                real_indicators.append("Реальные данные скриншота")
                
        verdict = "❌ ФИКТИВНЫЙ" if is_fake else "✅ РЕАЛЬНЫЙ" if real_indicators else "⚠️ СОМНИТЕЛЬНЫЙ"
        
        print(f"   Результат: {verdict}")
        print(f"   Успех: {success}, Размер: {data_size} байт")
        if fake_indicators:
            print(f"   🚨 Индикаторы подделки: {fake_indicators}")
        if real_indicators:
            print(f"   ✅ Индикаторы реальности: {real_indicators}")
            
        return {"tool": "computer_use_tool", "success": success, "fake": is_fake, "size": data_size}
    
    def _create_test_image(self):
        """Создание тестового изображения"""
        try:
            from PIL import Image
            
            # Создаём простое изображение 100x100 красного цвета
            img = Image.new('RGB', (100, 100), color='red')
            
            temp_dir = Path(tempfile.gettempdir())
            img_path = temp_dir / 'kittycore_test_image.png'
            img.save(img_path)
            
            return img_path
        except ImportError:
            # Если PIL недоступен, создаём текстовый файл как заглушку
            temp_dir = Path(tempfile.gettempdir()) 
            img_path = temp_dir / 'kittycore_test_fake.txt'
            img_path.write_text("Fake image for testing")
            return img_path
    
    def run_all_tests(self):
        """Запуск всех честных тестов"""
        print("🕵️ ЧЕСТНАЯ ПРОВЕРКА ВСЕХ ИНСТРУМЕНТОВ KITTYCORE 3.0")
        print("Цель: Выявить фиктивные результаты и мок-ответы")
        print("=" * 70)
        
        tests = [
            self.test_enhanced_web_search,
            self.test_media_tool,
            self.test_email_tool,
            self.test_network_tool,
            self.test_computer_use_tool
        ]
        
        start_time = time.time()
        results = []
        
        for test in tests:
            print()
            try:
                result = test()
                results.append(result)
            except Exception as e:
                print(f"   💥 Исключение: {e}")
                results.append({"tool": test.__name__, "success": False, "fake": True, "size": 0})
                
        total_time = time.time() - start_time
        
        # Анализ результатов
        print("\n" + "=" * 70)
        print("🎯 АНАЛИЗ ЧЕСТНОСТИ ИНСТРУМЕНТОВ")
        print("-" * 50)
        
        real_tools = 0
        fake_tools = 0
        suspicious_tools = 0
        
        for result in results:
            tool_name = result['tool']
            if result.get('fake', False):
                status = "❌ ФИКТИВНЫЙ"
                fake_tools += 1
            elif result.get('success', False):
                status = "✅ РЕАЛЬНЫЙ"
                real_tools += 1
            else:
                status = "⚠️ СОМНИТЕЛЬНЫЙ"
                suspicious_tools += 1
                
            size = result.get('size', 0)
            print(f"{tool_name:25} {status} ({size} байт)")
        
        total_tools = len(results)
        print("-" * 50)
        print(f"✅ РЕАЛЬНЫЕ:      {real_tools}/{total_tools} ({real_tools/total_tools*100:.1f}%)")
        print(f"❌ ФИКТИВНЫЕ:     {fake_tools}/{total_tools} ({fake_tools/total_tools*100:.1f}%)")
        print(f"⚠️ СОМНИТЕЛЬНЫЕ:  {suspicious_tools}/{total_tools} ({suspicious_tools/total_tools*100:.1f}%)")
        print(f"⏱️ ВРЕМЯ:         {total_time:.1f} секунд")
        
        if fake_tools > 0:
            print(f"\n🚨 ОБНАРУЖЕНЫ ФИКТИВНЫЕ РЕЗУЛЬТАТЫ: {fake_tools} инструментов!")
            print("   Требуется исправление этих инструментов.")
        else:
            print("\n🎉 ВСЕ ИНСТРУМЕНТЫ ЧЕСТНЫЕ!")
        
        return results

def main():
    """Главная функция"""
    checker = HonestToolsChecker()
    results = checker.run_all_tests()
    
    # Определяем общий результат
    fake_count = sum(1 for r in results if r.get('fake', False))
    
    if fake_count == 0:
        print("\n✅ Все инструменты прошли проверку на честность!")
        exit(0)
    else:
        print(f"\n❌ Обнаружены фиктивные результаты в {fake_count} инструментах")
        exit(1)

if __name__ == "__main__":
    main() 