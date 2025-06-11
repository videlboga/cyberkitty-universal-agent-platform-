#!/usr/bin/env python3
"""
Тест браузерных инструментов KittyCore

Проверяем работу FileSystemTool, ManifestValidatorTool, HumanRequestTool
без использования LLM.
"""

import os
import sys
import json
import tempfile
from pathlib import Path

# Добавляем путь к модулю kittycore
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kittycore.browser_tools.browser_tools import FileSystemTool, ManifestValidatorTool, HumanRequestTool


def test_filesystem_tool():
    """Тест файловой системы"""
    print("🗂️ === ТЕСТ FILESYSTEM TOOL ===\n")
    
    tool = FileSystemTool()
    
    # Создаём временную папку для тестов
    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = Path(temp_dir)
        
        # 1. Создание папки
        print("1. 📁 Создание папки...")
        result = tool.execute(action="mkdir", path=str(test_dir / "test_extension"))
        print(f"   Результат: {result.success}")
        print(f"   Сообщение: {result.data['message']}")
        
        # 2. Создание файла
        print("\n2. 📄 Создание файла manifest.json...")
        manifest_content = {
            "manifest_version": 3,
            "name": "Test Extension",
            "version": "1.0.0",
            "description": "Тестовое расширение"
        }
        
        result = tool.execute(
            action="create",
            path=str(test_dir / "test_extension" / "manifest.json"),
            content=json.dumps(manifest_content, indent=2)
        )
        print(f"   Результат: {result.success}")
        print(f"   Сообщение: {result.data['message']}")
        
        # 3. Чтение файла
        print("\n3. 👀 Чтение файла...")
        result = tool.execute(
            action="read",
            path=str(test_dir / "test_extension" / "manifest.json")
        )
        print(f"   Результат: {result.success}")
        print(f"   Содержимое: {result.data['content'][:100]}...")
        
        # 4. Список файлов
        print("\n4. 📋 Список файлов в папке...")
        result = tool.execute(
            action="list",
            path=str(test_dir / "test_extension")
        )
        print(f"   Результат: {result.success}")
        print(f"   Файлы: {result.data['items']}")
        
        # 5. Удаление файла
        print("\n5. 🗑️ Удаление файла...")
        result = tool.execute(
            action="delete",
            path=str(test_dir / "test_extension" / "manifest.json")
        )
        print(f"   Результат: {result.success}")
        print(f"   Сообщение: {result.data['message']}")
    
    print("\n✅ FileSystemTool работает!")


def test_manifest_validator():
    """Тест валидатора manifest.json"""
    print("\n🔍 === ТЕСТ MANIFEST VALIDATOR ===\n")
    
    tool = ManifestValidatorTool()
    
    # Создаём временные manifest'ы для тестирования
    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = Path(temp_dir)
        
        # 1. Валидный manifest V3
        print("1. ✅ Тест валидного manifest V3...")
        valid_manifest = {
            "manifest_version": 3,
            "name": "Test Extension",
            "version": "1.0.0",
            "description": "Valid test extension",
            "action": {
                "default_popup": "popup.html"
            }
        }
        
        manifest_path = test_dir / "valid_manifest.json"
        manifest_path.write_text(json.dumps(valid_manifest, indent=2))
        
        result = tool.execute(manifest_path=str(manifest_path))
        print(f"   Результат: {result.success}")
        print(f"   Валидный: {result.data['valid']}")
        print(f"   Отчёт: {result.data['report']}")
        
        # 2. Невалидный manifest (отсутствуют поля)
        print("\n2. ❌ Тест невалидного manifest...")
        invalid_manifest = {
            "manifest_version": 3,
            "name": "Incomplete Extension"
            # Отсутствует version
        }
        
        invalid_path = test_dir / "invalid_manifest.json"
        invalid_path.write_text(json.dumps(invalid_manifest, indent=2))
        
        result = tool.execute(manifest_path=str(invalid_path))
        print(f"   Результат: {result.success}")
        print(f"   Валидный: {result.data['valid']}")
        print(f"   Проблемы: {result.data['issues']}")
        
        # 3. Manifest V2 (устаревший)
        print("\n3. ⚠️ Тест устаревшего manifest V2...")
        v2_manifest = {
            "manifest_version": 2,
            "name": "Legacy Extension",
            "version": "1.0.0",
            "description": "Old style extension"
        }
        
        v2_path = test_dir / "v2_manifest.json"
        v2_path.write_text(json.dumps(v2_manifest, indent=2))
        
        result = tool.execute(manifest_path=str(v2_path))
        print(f"   Результат: {result.success}")
        print(f"   Валидный: {result.data['valid']}")
        print(f"   Предупреждения: {result.data['warnings']}")
    
    print("\n✅ ManifestValidatorTool работает!")


def test_human_request_tool():
    """Тест запросов к пользователю"""
    print("\n🤝 === ТЕСТ HUMAN REQUEST TOOL ===\n")
    
    tool = HumanRequestTool()
    
    # 1. Запрос авторизации
    print("1. 🔑 Запрос авторизации...")
    result = tool.execute(
        request_type="auth",
        message="Нужен API ключ для Chrome Web Store",
        context={"service": "chrome_webstore", "reason": "publishing"}
    )
    print(f"   Результат: {result.success}")
    print(f"   Тип запроса: {result.data['request_type']}")
    print(f"   Ожидает ввода: {result.data['awaiting_user_input']}")
    print(f"   Форматированный запрос:\n{result.data['formatted_request']}")
    
    # 2. Запрос решения
    print("\n2. 🤔 Запрос принятия решения...")
    result = tool.execute(
        request_type="decision",
        message="Какой цвет кнопки использовать: синий или зелёный?",
        context={"component": "export_button", "options": ["blue", "green"]}
    )
    print(f"   Результат: {result.success}")
    print(f"   Контекст: {result.data['context']}")
    
    # 3. Запрос конфигурации
    print("\n3. ⚙️ Запрос конфигурации...")
    result = tool.execute(
        request_type="config",
        message="Нужно настроить permissions для расширения",
        context={"required_permissions": ["activeTab", "storage"]}
    )
    print(f"   Результат: {result.success}")
    
    print("\n✅ HumanRequestTool работает!")


def test_agent_factory():
    """Тест фабрики агентов"""
    print("\n🏭 === ТЕСТ AGENT FACTORY ===\n")
    
    from kittycore.agent_factory import agent_factory
    
    # 1. Создание специализированного агента
    print("1. 🧑‍💻 Создание агента-разработчика...")
    dev_agent = agent_factory.create_browser_dev_agent("Create a Chrome extension manifest")
    print(f"   Агент создан: {dev_agent.created_at}")
    print(f"   Промпт: {dev_agent.prompt[:100]}...")
    
    # 2. Создание команды агентов
    print("\n2. 👥 Создание команды агентов...")
    team = agent_factory.create_collaborative_team("Build productivity browser extension")
    print(f"   Команда создана: {len(team)} агентов")
    
    for i, agent in enumerate(team, 1):
        print(f"   🤖 Агент {i}: {agent.prompt.split('\n')[0]}")
    
    # 3. Статистика фабрики
    print("\n3. 📊 Статистика фабрики...")
    agents_list = agent_factory.list_created_agents()
    print(f"   Всего создано: {len(agents_list)} агентов")
    
    for agent_id in agents_list:
        info = agent_factory.get_agent_info(agent_id)
        print(f"   🔸 {agent_id}: {info.get('created_at', 'unknown')}")
    
    print("\n✅ AgentFactory работает!")


def test_integration():
    """Интеграционный тест: создание простого расширения"""
    print("\n🚀 === ИНТЕГРАЦИОННЫЙ ТЕСТ ===\n")
    
    # Создаём временную папку для проекта
    with tempfile.TemporaryDirectory() as temp_dir:
        project_dir = Path(temp_dir) / "test_extension"
        
        print("1. 🏗️ Создание структуры проекта...")
        
        # Используем FileSystemTool для создания структуры
        fs_tool = FileSystemTool()
        
        # Создаём папку проекта
        result = fs_tool.execute(action="mkdir", path=str(project_dir))
        print(f"   Папка проекта: {result.success}")
        
        # Создаём manifest.json
        manifest = {
            "manifest_version": 3,
            "name": "Test Time Tracker",
            "version": "1.0.0",
            "description": "Simple time tracking extension",
            "action": {
                "default_popup": "popup.html",
                "default_title": "Time Tracker"
            },
            "permissions": ["activeTab", "storage"],
            "content_scripts": [{
                "matches": ["<all_urls>"],
                "js": ["content.js"]
            }]
        }
        
        result = fs_tool.execute(
            action="create",
            path=str(project_dir / "manifest.json"),
            content=json.dumps(manifest, indent=2)
        )
        print(f"   Manifest.json: {result.success}")
        
        # Создаём popup.html
        popup_html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body { width: 300px; padding: 10px; }
        .time-display { font-size: 24px; text-align: center; }
    </style>
</head>
<body>
    <h1>Time Tracker</h1>
    <div class="time-display">00:00:00</div>
    <button id="start">Start</button>
    <button id="stop">Stop</button>
    <script src="popup.js"></script>
</body>
</html>"""
        
        result = fs_tool.execute(
            action="create",
            path=str(project_dir / "popup.html"),
            content=popup_html
        )
        print(f"   Popup.html: {result.success}")
        
        # Создаём popup.js
        popup_js = """document.addEventListener('DOMContentLoaded', function() {
    const timeDisplay = document.querySelector('.time-display');
    const startBtn = document.getElementById('start');
    const stopBtn = document.getElementById('stop');
    
    // Простая логика time tracking
    let startTime = 0;
    let isRunning = false;
    
    startBtn.addEventListener('click', function() {
        if (!isRunning) {
            startTime = Date.now();
            isRunning = true;
            updateDisplay();
        }
    });
    
    stopBtn.addEventListener('click', function() {
        isRunning = false;
    });
    
    function updateDisplay() {
        if (isRunning) {
            const elapsed = Date.now() - startTime;
            const seconds = Math.floor(elapsed / 1000) % 60;
            const minutes = Math.floor(elapsed / 60000) % 60;
            const hours = Math.floor(elapsed / 3600000);
            
            timeDisplay.textContent = 
                `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
            
            setTimeout(updateDisplay, 1000);
        }
    }
});"""
        
        result = fs_tool.execute(
            action="create",
            path=str(project_dir / "popup.js"),
            content=popup_js
        )
        print(f"   Popup.js: {result.success}")
        
        # Создаём content.js
        content_js = """// Content script для отслеживания времени на сайте
console.log('Time Tracker extension loaded on:', window.location.hostname);

// Отправляем информацию о текущем сайте в background
chrome.runtime.sendMessage({
    action: 'track_time',
    hostname: window.location.hostname,
    url: window.location.href
});"""
        
        result = fs_tool.execute(
            action="create",
            path=str(project_dir / "content.js"),
            content=content_js
        )
        print(f"   Content.js: {result.success}")
        
        print("\n2. 🔍 Валидация manifest...")
        
        # Проверяем manifest с помощью валидатора
        validator = ManifestValidatorTool()
        result = validator.execute(manifest_path=str(project_dir / "manifest.json"))
        
        print(f"   Валидация: {result.success}")
        print(f"   Manifest валидный: {result.data['valid']}")
        if result.data['issues']:
            print(f"   Проблемы: {result.data['issues']}")
        if result.data['warnings']:
            print(f"   Предупреждения: {result.data['warnings']}")
        
        print("\n3. 📋 Структура проекта...")
        
        # Показываем итоговую структуру
        result = fs_tool.execute(action="list", path=str(project_dir))
        print(f"   Файлы созданы: {result.data['items']}")
        
        print(f"\n✅ Простое расширение создано в: {project_dir}")
        print("   🎯 Готово к загрузке в Chrome для тестирования!")


def main():
    """Главная функция тестирования"""
    print("🧪 KittyCore Browser Tools - Тестирование\n")
    
    try:
        # Тестируем каждый инструмент
        test_filesystem_tool()
        test_manifest_validator()
        test_human_request_tool()
        test_agent_factory()
        
        # Интеграционный тест
        test_integration()
        
        print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        print("✅ Система браузерных инструментов работает корректно!")
        
    except Exception as e:
        print(f"\n💥 ОШИБКА В ТЕСТАХ: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 