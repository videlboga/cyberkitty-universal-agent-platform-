"""
Тесты для SecurityTool KittyCore 3.0
"""

import pytest
import asyncio
from unittest.mock import patch, MagicMock
from kittycore.tools.security_tool import (
    SecurityTool,
    SecurityVulnerability,
    PasswordAnalysis,
    HashAnalysis,
    SecurityAudit
)


class TestSecurityTool:
    """Тесты для SecurityTool"""
    
    @pytest.fixture
    def security_tool(self):
        """Фикстура для инструмента безопасности"""
        return SecurityTool()
    
    @pytest.mark.asyncio
    async def test_tool_initialization(self, security_tool):
        """Тест инициализации инструмента"""
        assert security_tool.name == "security_tool"
        assert "комплексный инструмент безопасности" in security_tool.description.lower()
        assert security_tool._vulnerability_patterns is not None
        assert security_tool._password_patterns is not None
        assert security_tool._hash_signatures is not None
    
    def test_available_actions(self, security_tool):
        """Тест списка доступных действий"""
        actions = security_tool.get_available_actions()
        
        expected_actions = [
            "scan_code_vulnerabilities",
            "analyze_password",
            "generate_secure_password", 
            "analyze_hash"
        ]
        
        for action in expected_actions:
            assert action in actions
    
    def test_vulnerability_patterns_loaded(self, security_tool):
        """Тест загрузки паттернов уязвимостей"""
        patterns = security_tool._vulnerability_patterns
        
        # Проверяем основные категории
        assert "sql_injection" in patterns
        assert "xss" in patterns
        assert "path_traversal" in patterns
        assert "hardcoded_secrets" in patterns
        assert "weak_crypto" in patterns
        
        # Проверяем структуру паттернов
        sql_patterns = patterns["sql_injection"]
        assert len(sql_patterns) > 0
        assert "pattern" in sql_patterns[0]
        assert "severity" in sql_patterns[0]
        assert "cwe" in sql_patterns[0]
    
    def test_detect_language(self, security_tool):
        """Тест определения языка программирования"""
        # Python код
        python_code = "def hello():\n    import os\n    print('Hello')"
        assert security_tool._detect_language(python_code) == "python"
        
        # JavaScript код
        js_code = "function hello() {\n    var name = 'test';\n    console.log(name);\n}"
        assert security_tool._detect_language(js_code) == "javascript"
        
        # PHP код
        php_code = "<?php\necho 'Hello World';\n?>"
        assert security_tool._detect_language(php_code) == "php"
        
        # По расширению файла
        assert security_tool._detect_language("", "test.py") == "python"
        assert security_tool._detect_language("", "test.js") == "javascript"
        
        # Неизвестный язык
        unknown_code = "some random text"
        assert security_tool._detect_language(unknown_code) == "unknown"


class TestPasswordAnalysis:
    """Тесты анализа паролей"""
    
    @pytest.fixture
    def security_tool(self):
        return SecurityTool()
    
    @pytest.mark.asyncio
    async def test_analyze_weak_password(self, security_tool):
        """Тест анализа слабого пароля"""
        result = await security_tool.analyze_password("123456")
        
        assert result.success is True
        data = result.data
        
        assert data["strength"] == "very_weak"
        assert data["score"] < 30
        assert data["length"] == 6
        assert data["has_digits"] is True
        assert data["has_lowercase"] is False
        assert data["has_uppercase"] is False
        assert data["has_special"] is False
        assert len(data["suggestions"]) > 0
    
    @pytest.mark.asyncio
    async def test_analyze_medium_password(self, security_tool):
        """Тест анализа среднего пароля"""
        result = await security_tool.analyze_password("Password123")
        
        assert result.success is True
        data = result.data
        
        assert data["strength"] in ["medium", "weak"]
        assert data["length"] == 11
        assert data["has_digits"] is True
        assert data["has_lowercase"] is True
        assert data["has_uppercase"] is True
        assert data["has_special"] is False
    
    @pytest.mark.asyncio
    async def test_analyze_strong_password(self, security_tool):
        """Тест анализа сильного пароля"""
        result = await security_tool.analyze_password("MyStr0ng!P@ssw0rd2024")
        
        assert result.success is True
        data = result.data
        
        assert data["strength"] in ["strong", "very_strong"]
        assert data["score"] >= 70
        assert data["length"] == 21
        assert data["has_digits"] is True
        assert data["has_lowercase"] is True
        assert data["has_uppercase"] is True
        assert data["has_special"] is True
        assert data["entropy"] > 60
    
    @pytest.mark.asyncio
    async def test_analyze_common_password(self, security_tool):
        """Тест анализа распространённого пароля"""
        result = await security_tool.analyze_password("password")
        
        assert result.success is True
        data = result.data
        
        # Распространённые пароли должны получать низкую оценку
        assert data["strength"] in ["very_weak", "weak"]
        assert "распространённые пароли" in " ".join(data["suggestions"]).lower() or \
               "не используйте" in " ".join(data["suggestions"]).lower()
    
    def test_calculate_password_entropy(self, security_tool):
        """Тест вычисления энтропии пароля"""
        # Только цифры
        entropy1 = security_tool._calculate_password_entropy("123456")
        assert entropy1 > 0
        
        # Буквы + цифры + спецсимволы
        entropy2 = security_tool._calculate_password_entropy("Abc123!@#")
        assert entropy2 > entropy1
        
        # Пустой пароль
        entropy3 = security_tool._calculate_password_entropy("")
        assert entropy3 == 0.0
    
    def test_estimate_crack_time(self, security_tool):
        """Тест оценки времени взлома"""
        # Слабая энтропия
        time1 = security_tool._estimate_crack_time(15.0)
        assert "мгновенно" in time1.lower() or "секунд" in time1.lower()
        
        # Высокая энтропия
        time2 = security_tool._estimate_crack_time(80.0)
        assert "столетия" in time2.lower() or "лет" in time2.lower()


class TestPasswordGeneration:
    """Тесты генерации паролей"""
    
    @pytest.fixture
    def security_tool(self):
        return SecurityTool()
    
    @pytest.mark.asyncio
    async def test_generate_default_password(self, security_tool):
        """Тест генерации пароля с настройками по умолчанию"""
        result = await security_tool.generate_secure_password()
        
        assert result.success is True
        data = result.data
        
        password = data["password"]
        assert len(password) == 16  # длина по умолчанию
        assert data["generation_method"] == "cryptographically_secure"
        assert data["charset_size"] > 0
        assert data["analysis"] is not None
    
    @pytest.mark.asyncio
    async def test_generate_custom_password(self, security_tool):
        """Тест генерации пароля с кастомными настройками"""
        result = await security_tool.generate_secure_password(
            length=12,
            include_uppercase=True,
            include_lowercase=True,
            include_digits=False,
            include_special=False
        )
        
        assert result.success is True
        data = result.data
        
        password = data["password"]
        assert len(password) == 12
        
        # Проверяем что есть только буквы
        assert any(c.islower() for c in password)
        assert any(c.isupper() for c in password)
        assert not any(c.isdigit() for c in password)
        assert not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
    
    @pytest.mark.asyncio
    async def test_generate_password_validation(self, security_tool):
        """Тест валидации параметров генерации пароля"""
        # Слишком короткий пароль
        result = await security_tool.generate_secure_password(length=4)
        assert result.success is False
        assert "не менее 8 символов" in result.error
        
        # Все опции отключены
        result = await security_tool.generate_secure_password(
            include_uppercase=False,
            include_lowercase=False,
            include_digits=False,
            include_special=False
        )
        assert result.success is False
        assert "недостаточно символов" in result.error.lower()


if __name__ == "__main__":
    # Запуск тестов
    pytest.main([__file__, "-v"])


class TestCodeScanning:
    """Тесты сканирования кода на уязвимости"""
    
    @pytest.fixture
    def security_tool(self):
        return SecurityTool()
    
    @pytest.mark.asyncio
    async def test_scan_sql_injection(self, security_tool):
        """Тест обнаружения SQL инъекции"""
        vulnerable_code = '''
def get_user(user_id):
    query = "SELECT * FROM users WHERE id = '" + user_id + "'"
    return execute(query)
        '''
        
        result = await security_tool.scan_code_vulnerabilities(code=vulnerable_code)
        
        assert result.success is True
        data = result.data
        
        # Должна быть найдена минимум одна уязвимость SQL injection
        vulns = data["audit"]["vulnerabilities"]
        sql_vulns = [v for v in vulns if v["category"] == "sql_injection"]
        assert len(sql_vulns) > 0
        
        # Проверяем структуру уязвимости
        vuln = sql_vulns[0]
        assert vuln["severity"] == "high"
        assert "CWE-89" in vuln["cwe_id"]
        assert "Line" in vuln["location"]
    
    @pytest.mark.asyncio
    async def test_scan_xss_vulnerability(self, security_tool):
        """Тест обнаружения XSS уязвимости"""
        vulnerable_code = '''
function updateContent(userInput) {
    document.getElementById("content").innerHTML = userInput + "<br>";
}
        '''
        
        result = await security_tool.scan_code_vulnerabilities(code=vulnerable_code)
        
        assert result.success is True
        data = result.data
        
        # Должна быть найдена XSS уязвимость
        vulns = data["audit"]["vulnerabilities"]
        xss_vulns = [v for v in vulns if v["category"] == "xss"]
        assert len(xss_vulns) > 0
        
        vuln = xss_vulns[0]
        assert vuln["severity"] == "medium"
        assert "CWE-79" in vuln["cwe_id"]
    
    @pytest.mark.asyncio
    async def test_scan_hardcoded_secrets(self, security_tool):
        """Тест обнаружения hardcoded секретов"""
        vulnerable_code = '''
def connect_db():
    password = "super_secret_password123"
    api_key = "sk-1234567890abcdef"
    return connect(password=password, api_key=api_key)
        '''
        
        result = await security_tool.scan_code_vulnerabilities(code=vulnerable_code)
        
        assert result.success is True
        data = result.data
        
        # Должны быть найдены hardcoded секреты
        vulns = data["audit"]["vulnerabilities"]
        secret_vulns = [v for v in vulns if v["category"] == "hardcoded_secrets"]
        assert len(secret_vulns) >= 1  # Как минимум пароль или API ключ
        
        vuln = secret_vulns[0]
        assert vuln["severity"] == "high"
        assert "CWE-798" in vuln["cwe_id"]
    
    @pytest.mark.asyncio
    async def test_scan_clean_code(self, security_tool):
        """Тест сканирования чистого кода без уязвимостей"""
        clean_code = '''
def safe_function(user_input):
    # Валидация входных данных
    if not validate_input(user_input):
        logger.warning("Invalid input detected")
        return None
    
    # Параметризованный запрос
    query = "SELECT * FROM users WHERE id = ?"
    return db.execute(query, (user_input,))
        '''
        
        result = await security_tool.scan_code_vulnerabilities(code=clean_code)
        
        assert result.success is True
        data = result.data
        
        # В чистом коде не должно быть критических уязвимостей
        audit = data["audit"]
        assert audit["security_score"] >= 80
        assert audit["risk_level"] in ["low", "medium"]
        
        # Проверяем compliance checks
        compliance = audit["compliance_checks"]
        assert compliance["has_input_validation"] is True
        assert compliance["has_logging"] is True
    
    @pytest.mark.asyncio
    async def test_scan_from_file_not_found(self, security_tool):
        """Тест сканирования несуществующего файла"""
        result = await security_tool.scan_code_vulnerabilities(
            file_path="/path/to/nonexistent/file.py"
        )
        
        assert result.success is False
        assert "файл не найден" in result.error.lower()
    
    @pytest.mark.asyncio
    async def test_scan_missing_parameters(self, security_tool):
        """Тест сканирования без параметров"""
        result = await security_tool.scan_code_vulnerabilities()
        
        assert result.success is False
        assert "необходимо указать" in result.error.lower()


class TestHashAnalysis:
    """Тесты анализа хешей"""
    
    @pytest.fixture
    def security_tool(self):
        return SecurityTool()
    
    @pytest.mark.asyncio
    async def test_analyze_md5_hash(self, security_tool):
        """Тест анализа MD5 хеша"""
        md5_hash = "5d41402abc4b2a76b9719d911017c592"  # hello
        
        result = await security_tool.analyze_hash(md5_hash)
        
        assert result.success is True
        data = result.data
        
        assert data["hash_length"] == 32
        assert "MD5" in data["possible_algorithms"]
        assert data["format_type"] == "hex"
        assert data["is_salted"] is False
        assert data["confidence"] > 0.5
    
    @pytest.mark.asyncio
    async def test_analyze_sha256_hash(self, security_tool):
        """Тест анализа SHA256 хеша"""
        sha256_hash = "2cf24dba4f21d4288094c93dbfd1075ab63a1e3e5e0e0e3b6b5c3e6c"  # hello (неполный для примера)
        sha256_hash = "2cf24dba4f21d4288094c93dbfd1075ab63a1e3e5e0e0e3b6b5c3e6c19"  # 66 символов
        
        result = await security_tool.analyze_hash(sha256_hash)
        
        assert result.success is True
        data = result.data
        
        assert data["hash_length"] == 58
        assert data["format_type"] == "hex"
    
    @pytest.mark.asyncio
    async def test_analyze_salted_hash(self, security_tool):
        """Тест анализа хеша с солью"""
        salted_hash = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj"
        
        result = await security_tool.analyze_hash(salted_hash)
        
        assert result.success is True
        data = result.data
        
        assert data["is_salted"] is True  # Разделитель $ указывает на соль
    
    @pytest.mark.asyncio
    async def test_analyze_unknown_hash(self, security_tool):
        """Тест анализа неизвестного хеша"""
        unknown_hash = "abc123xyz"  # Короткий и нестандартный
        
        result = await security_tool.analyze_hash(unknown_hash)
        
        assert result.success is True
        data = result.data
        
        assert "Unknown" in data["possible_algorithms"]
        assert data["confidence"] < 0.5
    
    def test_detect_salt(self, security_tool):
        """Тест определения соли в хешах"""
        # Хеш с разделителями (bcrypt формат)
        assert security_tool._detect_salt("$2b$12$abc123") is True
        
        # Стандартный MD5 без соли
        assert security_tool._detect_salt("5d41402abc4b2a76b9719d911017c592") is False
        
        # Хеш с двоеточием (shadow формат)
        assert security_tool._detect_salt("user:hash:salt") is True
    
    def test_calculate_hash_confidence(self, security_tool):
        """Тест вычисления уверенности определения хеша"""
        # Хорошо определяемый хеш
        confidence1 = security_tool._calculate_hash_confidence(
            "5d41402abc4b2a76b9719d911017c592", ["MD5"]
        )
        assert confidence1 > 0.7
        
        # Неизвестный хеш
        confidence2 = security_tool._calculate_hash_confidence(
            "unknown", ["Unknown"]
        )
        assert confidence2 < 0.2
        
        # Множество возможных алгоритмов
        confidence3 = security_tool._calculate_hash_confidence(
            "64chars", ["SHA256", "Blake2s", "Other1", "Other2"]
        )
        assert confidence3 < 0.6


class TestSecurityToolIntegration:
    """Интеграционные тесты SecurityTool"""
    
    @pytest.fixture
    def security_tool(self):
        return SecurityTool()
    
    @pytest.mark.asyncio
    async def test_execute_method(self, security_tool):
        """Тест метода execute с различными действиями"""
        # Тест анализа пароля
        result = await security_tool.execute("analyze_password", password="test123")
        assert result.success is True
        
        # Тест генерации пароля
        result = await security_tool.execute("generate_secure_password", length=12)
        assert result.success is True
        
        # Тест анализа хеша
        result = await security_tool.execute("analyze_hash", hash_value="5d41402abc4b2a76b9719d911017c592")
        assert result.success is True
        
        # Тест неизвестного действия
        result = await security_tool.execute("unknown_action")
        assert result.success is False
        assert "неизвестное действие" in result.error.lower()
    
    def test_get_schema(self, security_tool):
        """Тест схемы инструмента"""
        schema = security_tool.get_schema()
        
        assert schema["type"] == "object"
        assert "action" in schema["properties"]
        assert "action" in schema["required"]
        
        # Проверяем основные свойства
        properties = schema["properties"]
        assert "password" in properties
        assert "hash_value" in properties
        assert "code" in properties
        assert "file_path" in properties
        
        # Проверяем enum для действий
        actions_enum = properties["action"]["enum"]
        assert "analyze_password" in actions_enum
        assert "scan_code_vulnerabilities" in actions_enum
        assert "analyze_hash" in actions_enum


if __name__ == "__main__":
    # Запуск тестов
    pytest.main([__file__, "-v"]) 