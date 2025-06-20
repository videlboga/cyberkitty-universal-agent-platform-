"""
🧪 Тесты для SuperSystemTool - Мощнейшего системного инструмента KittyCore 3.0

Проверяем:
- Объединённые системные операции (все в одном)
- Безопасность файловых операций  
- Мониторинг ресурсов
- Health check
- Валидацию и error handling
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

from kittycore.tools.super_system_tool import SuperSystemTool


class TestSuperSystemTool:
    """Тесты SuperSystemTool - единственного системного инструмента"""
    
    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.tool = SuperSystemTool()
        # Используем рабочую директорию вместо /tmp
        self.temp_dir = os.path.join(os.getcwd(), "test_temp")
        os.makedirs(self.temp_dir, exist_ok=True)
        self.temp_file = os.path.join(self.temp_dir, "test.txt")
    
    def teardown_method(self):
        """Очистка после теста"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    # ========================================
    # 🖥️ СИСТЕМНАЯ ИНФОРМАЦИЯ
    # ========================================
    
    def test_get_system_info(self):
        """Тест получения системной информации"""
        result = self.tool.execute("get_system_info")
        
        assert result.success is True
        assert "system_info" in result.data
        
        data = result.data["system_info"]
        assert "platform" in data
        assert "hostname" in data
        assert "cpu_count" in data
        assert "memory_total_gb" in data
        assert isinstance(data["cpu_count"], int)
        assert data["cpu_count"] > 0
    
    def test_get_resource_usage(self):
        """Тест мониторинга ресурсов"""
        result = self.tool.execute("get_resource_usage")
        
        assert result.success is True
        assert "resource_usage" in result.data
        
        data = result.data["resource_usage"]
        assert "cpu_percent" in data
        assert "memory_percent" in data
        assert "disk_usage_percent" in data
        assert "top_processes" in data
        
        assert 0 <= data["cpu_percent"] <= 100
        assert 0 <= data["memory_percent"] <= 100
        assert isinstance(data["top_processes"], list)
    
    def test_health_check(self):
        """Тест health check системы"""
        result = self.tool.execute("health_check")
        
        assert result.success is True
        data = result.data
        
        assert "overall_status" in data
        assert data["overall_status"] in ["good", "warning", "critical"]
        
        assert "cpu" in data
        assert "memory" in data
        assert "disk" in data
        
        assert "status" in data["cpu"]
        assert "usage_percent" in data["cpu"]
    
    # ========================================
    # 📂 ПРОЦЕССЫ
    # ========================================
    
    def test_get_processes(self):
        """Тест получения списка процессов"""
        result = self.tool.execute("get_processes", limit=5)
        
        assert result.success is True
        assert "processes" in result.data
        
        processes = result.data["processes"]
        assert isinstance(processes, list)
        assert len(processes) <= 5
        
        if processes:
            proc = processes[0]
            assert "pid" in proc
            assert "name" in proc
            assert "cpu_percent" in proc
    
    @patch('subprocess.run')
    def test_run_command_safe(self, mock_run):
        """Тест выполнения безопасной команды"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="Hello World",
            stderr="",
            args=["echo", "Hello World"]
        )
        
        result = self.tool.execute("run_command", command="echo Hello World")
        
        assert result.success is True
        assert "stdout" in result.data
        assert result.data["stdout"] == "Hello World"
    
    def test_run_command_blocked(self):
        """Тест блокировки опасной команды"""
        result = self.tool.execute("run_command", command="rm -rf /")
        
        assert result.success is False
        assert "потенциально опасной команды запрещено" in result.error.lower()
    
    # ========================================
    # 📁 ФАЙЛОВЫЕ ОПЕРАЦИИ (безопасные)
    # ========================================
    
    def test_safe_file_create_and_read(self):
        """Тест создания и чтения файла через safe_file методы"""
        content = "Hello, KittyCore SuperSystem!"
        
        # Создаём файл
        result = self.tool.execute("safe_file_create", path=self.temp_file, content=content)
        assert result.success is True
        assert os.path.exists(self.temp_file)
        
        # Читаем файл
        result = self.tool.execute("safe_file_read", path=self.temp_file)
        assert result.success is True
        assert result.data["content"] == content
    
    def test_file_exists(self):
        """Тест проверки существования файла"""
        # Файл не существует
        result = self.tool.execute("file_exists", path="/nonexistent/file.txt")
        assert result.success is True
        assert result.data["exists"] is False
        
        # Создаём файл
        with open(self.temp_file, 'w') as f:
            f.write("test")
        
        # Файл существует
        result = self.tool.execute("file_exists", path=self.temp_file)
        assert result.success is True
        assert result.data["exists"] is True
    
    def test_safe_file_list(self):
        """Тест безопасного листинга директории"""
        # Создаём тестовые файлы
        test_files = ["file1.txt", "file2.py", "file3.json"]
        for filename in test_files:
            filepath = os.path.join(self.temp_dir, filename)
            with open(filepath, 'w') as f:
                f.write("test")
        
        result = self.tool.execute("safe_file_list", path=self.temp_dir)
        
        assert result.success is True
        assert "files" in result.data
        
        files = result.data["files"]
        found_files = [f["name"] for f in files if f.get("is_file")]
        
        for test_file in test_files:
            assert test_file in found_files
    
    def test_copy_file(self):
        """Тест копирования файла"""
        content = "Test content"
        destination = os.path.join(self.temp_dir, "copied.txt")
        
        # Создаём исходный файл
        with open(self.temp_file, 'w') as f:
            f.write(content)
        
        # Копируем
        result = self.tool.execute("copy_file", path=self.temp_file, destination=destination)
        
        assert result.success is True
        assert os.path.exists(destination)
        
        # Проверяем содержимое
        with open(destination, 'r') as f:
            assert f.read() == content
    
    def test_delete_file(self):
        """Тест удаления файла"""
        # Создаём файл
        with open(self.temp_file, 'w') as f:
            f.write("test")
        
        assert os.path.exists(self.temp_file)
        
        # Удаляем
        result = self.tool.execute("delete_file", path=self.temp_file)
        
        assert result.success is True
        assert not os.path.exists(self.temp_file)
    
    # ========================================
    # 🛡️ БЕЗОПАСНОСТЬ
    # ========================================
    
    def test_validate_file_path_safe(self):
        """Тест валидации безопасного пути"""
        safe_path = os.path.join(self.temp_dir, "safe.txt")
        
        result = self.tool.execute("validate_file_path", path=safe_path)
        
        assert result.success is True
        assert result.data["validation_passed"] is True
        assert result.data["is_safe_extension"] is True
    
    def test_validate_file_path_unsafe_extension(self):
        """Тест валидации небезопасного расширения"""
        unsafe_path = os.path.join(self.temp_dir, "malware.exe")
        
        result = self.tool.execute("validate_file_path", path=unsafe_path)
        
        assert result.success is True
        assert result.data["validation_passed"] is False
        assert result.data["is_safe_extension"] is False
    
    def test_validate_file_path_system_directory(self):
        """Тест валидации системной директории"""
        result = self.tool.execute("validate_file_path", path="/etc/passwd")
        
        assert result.success is True
        assert result.data["validation_passed"] is False
        assert result.data["is_safe_path"] is False
    
    def test_check_file_safety(self):
        """Тест проверки безопасности файла"""
        # Создаём безопасный файл
        with open(self.temp_file, 'w') as f:
            f.write("safe content")
        
        result = self.tool.execute("check_file_safety", path=self.temp_file)
        
        assert result.success is True
        assert result.data["overall_safe"] is True
        assert result.data["extension_safe"] is True
        assert result.data["size_safe"] is True
    
    # ========================================
    # 🔍 МОНИТОРИНГ
    # ========================================
    
    def test_monitoring_lifecycle(self):
        """Тест жизненного цикла мониторинга"""
        # Запускаем мониторинг
        result = self.tool.execute("start_monitoring", interval=0.1)
        assert result.success is True
        
        # Ждём немного
        import time
        time.sleep(0.3)
        
        # Получаем данные
        result = self.tool.execute("get_monitoring_data")
        assert result.success is True
        assert result.data["monitoring_active"] is True
        assert result.data["data_points_count"] > 0
        
        # Останавливаем
        result = self.tool.execute("stop_monitoring")
        assert result.success is True
        assert result.data["monitoring_stopped"] is True
    
    # ========================================
    # ❌ ERROR HANDLING
    # ========================================
    
    def test_invalid_action(self):
        """Тест неверного действия"""
        result = self.tool.execute("invalid_action")
        
        assert result.success is False
        assert "неизвестное действие" in result.error.lower()
    
    def test_file_not_found(self):
        """Тест несуществующего файла"""
        nonexistent_file = os.path.join(self.temp_dir, "nonexistent.txt")
        result = self.tool.execute("read_file", path=nonexistent_file)
        
        assert result.success is False
        assert "не найден" in result.error.lower()
    
    def test_invalid_pid(self):
        """Тест несуществующего процесса"""
        result = self.tool.execute("get_process_info", pid=999999)
        
        assert result.success is False
        assert "не найден" in result.error.lower()
    
    # ========================================
    # 🧠 ИНТЕГРАЦИЯ
    # ========================================
    
    def test_tool_name_and_description(self):
        """Тест базовых свойств инструмента"""
        assert self.tool.name == "super_system_tool"
        assert "мощнейший системный инструмент" in self.tool.description.lower()
    
    def test_schema_validation(self):
        """Тест JSON схемы"""
        schema = self.tool.get_schema()
        
        assert "type" in schema
        assert schema["type"] == "object"
        assert "properties" in schema
        assert "action" in schema["properties"]
        
        actions = schema["properties"]["action"]["enum"]
        expected_actions = [
            "get_system_info", "get_resource_usage", "health_check",
            "get_processes", "run_command", "safe_file_create", "safe_file_read",
            "validate_file_path", "start_monitoring"
        ]
        
        for action in expected_actions:
            assert action in actions


# ========================================
# 🏃 ИНТЕГРАЦИОННЫЕ ТЕСТЫ
# ========================================

class TestSuperSystemToolIntegration:
    """Интеграционные тесты SuperSystemTool"""
    
    def setup_method(self):
        self.tool = SuperSystemTool()
    
    def test_system_info_and_monitoring_flow(self):
        """Тест полного флоу: информация + мониторинг + health check"""
        # 1. Получаем системную информацию
        sys_info = self.tool.execute("get_system_info")
        assert sys_info.success is True
        
        # 2. Проверяем ресурсы
        resources = self.tool.execute("get_resource_usage")
        assert resources.success is True
        
        # 3. Health check
        health = self.tool.execute("health_check")
        assert health.success is True
        
        # Все операции успешны
        assert all([sys_info.success, resources.success, health.success])
    
    def test_file_operations_flow(self):
        """Тест полного флоу файловых операций"""
        # Используем безопасную директорию
        temp_dir = os.path.join(os.getcwd(), "test_integration_temp")
        os.makedirs(temp_dir, exist_ok=True)
        test_file = os.path.join(temp_dir, "flow_test.txt")
        test_content = "SuperSystemTool Flow Test"
        
        try:
            # 1. Создаём файл
            create_result = self.tool.execute("safe_file_create", path=test_file, content=test_content)
            assert create_result.success is True
            
            # 2. Проверяем существование
            exists_result = self.tool.execute("file_exists", path=test_file)
            assert exists_result.success is True
            assert exists_result.data["exists"] is True
            
            # 3. Получаем информацию о файле
            info_result = self.tool.execute("file_info", path=test_file)
            assert info_result.success is True
            
            # 4. Читаем содержимое
            read_result = self.tool.execute("safe_file_read", path=test_file)
            assert read_result.success is True
            assert read_result.data["content"] == test_content
            
            # 5. Проверяем безопасность
            safety_result = self.tool.execute("check_file_safety", path=test_file)
            assert safety_result.success is True
            assert safety_result.data["overall_safe"] is True
            
        finally:
            # Очистка
            import shutil
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 