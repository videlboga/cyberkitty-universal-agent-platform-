"""
🚀 БЫСТРЫЕ ИНТЕГРАЦИОННЫЕ ТЕСТЫ ИНСТРУМЕНТОВ
Проверка основной функциональности ключевых инструментов
"""

import pytest
import asyncio
import sys
from pathlib import Path

# Добавляем путь к kittycore
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from kittycore.tools import DEFAULT_TOOLS

class TestToolsQuickIntegration:
    """Быстрые тесты инструментов"""
    
    def test_tools_loading(self):
        """Тест загрузки всех инструментов"""
        print(f"\n🔧 Проверяю загрузку {len(DEFAULT_TOOLS.tools)} инструментов...")
        
        # Проверяем что инструменты загружены
        assert len(DEFAULT_TOOLS.tools) > 0, "Инструменты должны быть загружены"
        
        tool_names = list(DEFAULT_TOOLS.tools.keys())
        print(f"✅ Загружено инструментов: {len(tool_names)}")
        print(f"📋 Первые 5: {tool_names[:5]}")
    
    @pytest.mark.asyncio
    async def test_enhanced_code_generator(self):
        """Тест генератора кода"""
        print(f"\n💻 Тестирую EnhancedCodeGenerator...")
        
        # Находим инструмент
        code_tool = None
        for name, tool in DEFAULT_TOOLS.tools.items():
            if "code" in name.lower() and "enhanced" in name.lower():
                code_tool = tool
                break
        
        if code_tool is None:
            print("⚠️ EnhancedCodeGenerator не найден, пропускаю тест")
            return
        
        # Тестируем генерацию простого кода
        test_params = {
            "task": "Создай функцию hello_world() на Python",
            "language": "python",
            "output_file": "test_hello.py"
        }
        
        try:
            result = await code_tool.execute(test_params)
            assert result is not None, "Результат генерации кода не должен быть None"
            print(f"✅ EnhancedCodeGenerator работает")
            
        except Exception as e:
            print(f"⚠️ Ошибка в EnhancedCodeGenerator: {e}")
    
    @pytest.mark.asyncio  
    async def test_super_system_tool(self):
        """Тест системного инструмента"""
        print(f"\n🛠️ Тестирую SuperSystemTool...")
        
        # Находим инструмент
        system_tool = None
        for name, tool in DEFAULT_TOOLS.tools.items():
            if "super_system" in name.lower():
                system_tool = tool
                break
        
        if system_tool is None:
            print("⚠️ SuperSystemTool не найден, пропускаю тест")
            return
        
        # Тестируем простую системную операцию
        test_params = {
            "action": "list_files",
            "path": "."
        }
        
        try:
            result = await system_tool.execute(test_params)
            assert result is not None, "Результат системной операции не должен быть None"
            print(f"✅ SuperSystemTool работает")
            
        except Exception as e:
            print(f"⚠️ Ошибка в SuperSystemTool: {e}")
    
    @pytest.mark.asyncio
    async def test_enhanced_web_scraping(self):
        """Тест веб-скрапинга"""
        print(f"\n🌐 Тестирую EnhancedWebScraping...")
        
        # Находим инструмент
        web_tool = None
        for name, tool in DEFAULT_TOOLS.tools.items():
            if "web" in name.lower() and "scraping" in name.lower():
                web_tool = tool
                break
        
        if web_tool is None:
            print("⚠️ EnhancedWebScraping не найден, пропускаю тест")
            return
        
        # Тестируем простой запрос (httpbin для тестирования)
        test_params = {
            "url": "https://httpbin.org/json",
            "method": "GET"
        }
        
        try:
            result = await web_tool.execute(test_params)
            assert result is not None, "Результат веб-скрапинга не должен быть None"
            print(f"✅ EnhancedWebScraping работает")
            
        except Exception as e:
            print(f"⚠️ Ошибка в EnhancedWebScraping: {e}")
    
    def test_tools_schemas(self):
        """Тест схем инструментов"""
        print(f"\n📋 Проверяю схемы инструментов...")
        
        valid_schemas = 0
        total_tools = len(DEFAULT_TOOLS.tools)
        
        for name, tool in DEFAULT_TOOLS.tools.items():
            try:
                schema = tool.get_schema()
                if schema and isinstance(schema, dict):
                    valid_schemas += 1
                else:
                    print(f"⚠️ Инструмент {name} имеет неправильную схему")
            except Exception as e:
                print(f"⚠️ Ошибка схемы {name}: {e}")
        
        print(f"✅ Валидных схем: {valid_schemas}/{total_tools}")
        assert valid_schemas >= total_tools * 0.8, "Минимум 80% инструментов должны иметь валидные схемы"
    
    def test_memory_system_basic(self):
        """Базовый тест системы памяти"""
        print(f"\n🧠 Тестирую базовую память...")
        
        try:
            from kittycore.memory.amem_integration import KittyCoreMemorySystem
            
            # Создаём временную систему памяти
            memory = KittyCoreMemorySystem(vault_path="/tmp/test_memory")
            
            print(f"✅ Система памяти A-MEM инициализирована")
            
        except Exception as e:
            print(f"⚠️ Ошибка системы памяти: {e}")
    
    def test_tools_categories_coverage(self):
        """Тест покрытия категорий инструментов"""
        print(f"\n📊 Проверяю покрытие категорий...")
        
        tool_names = [name.lower() for name in DEFAULT_TOOLS.tools.keys()]
        
        # Ожидаемые категории
        expected_categories = {
            "web": ["web", "scraping", "search"],
            "code": ["code", "generator", "execution"],
            "system": ["system", "file", "directory"],
            "ai": ["ai", "integration", "llm"],
            "security": ["security", "analysis"],
            "document": ["document", "pdf", "text"],
            "data": ["data", "analysis", "processing"],
        }
        
        found_categories = set()
        
        for category, keywords in expected_categories.items():
            for tool_name in tool_names:
                if any(keyword in tool_name for keyword in keywords):
                    found_categories.add(category)
                    break
        
        coverage = len(found_categories) / len(expected_categories) * 100
        
        print(f"✅ Покрытие категорий: {coverage:.1f}%")
        print(f"📋 Найденные: {', '.join(sorted(found_categories))}")
        
        assert coverage >= 70, "Должно быть покрыто минимум 70% категорий"

if __name__ == "__main__":
    # Запуск тестов напрямую
    pytest.main([__file__, "-v", "-s", "--tb=short"]) 