"""
SecurityTool - Продвинутый инструмент безопасности для KittyCore 3.0

Обеспечивает комплексную безопасность:
- Сканирование уязвимостей кода
- Анализ безопасности веб-приложений
- Проверка паролей и хешей
- Анализ сетевой безопасности
- Детекция вредоносного контента
- Аудит конфигураций безопасности
"""

import hashlib
import hmac
import secrets
import re
import json
import time
import base64
import urllib.parse
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Dict, Any, List, Optional, Union, Set, Tuple
from pathlib import Path
import subprocess

from loguru import logger

from kittycore.tools.base_tool import Tool, ToolResult


@dataclass
class SecurityVulnerability:
    """Уязвимость безопасности"""
    id: str
    title: str
    description: str
    severity: str  # critical, high, medium, low, info
    category: str  # injection, xss, auth, crypto, etc.
    location: str
    code_snippet: Optional[str] = None
    recommendation: Optional[str] = None
    cwe_id: Optional[str] = None
    cvss_score: Optional[float] = None


@dataclass
class PasswordAnalysis:
    """Анализ пароля"""
    password: str
    strength: str  # very_weak, weak, medium, strong, very_strong
    score: int  # 0-100
    length: int
    has_lowercase: bool
    has_uppercase: bool
    has_digits: bool
    has_special: bool
    entropy: float
    estimated_crack_time: str
    suggestions: List[str]


@dataclass
class HashAnalysis:
    """Анализ хеша"""
    hash_value: str
    possible_algorithms: List[str]
    hash_length: int
    format_type: str
    is_salted: bool
    confidence: float


@dataclass
class SecurityAudit:
    """Результат аудита безопасности"""
    target: str
    scan_type: str
    vulnerabilities: List[SecurityVulnerability]
    security_score: int  # 0-100
    risk_level: str  # low, medium, high, critical
    scan_duration: float
    recommendations: List[str]
    compliance_checks: Dict[str, bool]


class SecurityTool(Tool):
    """Продвинутый инструмент безопасности"""
    
    def __init__(self):
        super().__init__(
            name="security_tool",
            description="Комплексный инструмент безопасности - сканирование уязвимостей, анализ паролей, аудит безопасности"
        )
        
        # Базы данных уязвимостей
        self._vulnerability_patterns = self._load_vulnerability_patterns()
        self._password_patterns = self._load_password_patterns()
        self._hash_signatures = self._load_hash_signatures()
        
        # Настройки сканирования
        self._default_timeout = 30.0
        self._max_file_size = 10 * 1024 * 1024  # 10MB
        
        logger.info("🔒 SecurityTool инициализирован")
    
    def get_available_actions(self) -> List[str]:
        """Получение списка доступных действий"""
        return [
            "scan_code_vulnerabilities",
            "scan_web_vulnerabilities", 
            "analyze_password",
            "generate_secure_password",
            "analyze_hash",
            "crack_hash",
            "check_data_breach",
            "audit_file_permissions",
            "scan_network_vulnerabilities",
            "analyze_ssl_certificate",
            "check_security_headers",
            "validate_input",
            "encrypt_data",
            "decrypt_data",
            "generate_keys",
            "security_audit"
        ]
    
    def _load_vulnerability_patterns(self) -> Dict[str, List[Dict]]:
        """Загрузка паттернов уязвимостей"""
        return {
            "sql_injection": [
                {
                    "pattern": r"(\bSELECT\b.*?\bFROM\b.*?\bWHERE\b.*?['\"]?\s*\+\s*['\"]?)",
                    "severity": "high",
                    "cwe": "CWE-89",
                    "description": "Потенциальная SQL инъекция через конкатенацию строк"
                },
                {
                    "pattern": r"(execute\s*\(\s*['\"].*?['\"].*?\+.*?\))",
                    "severity": "high", 
                    "cwe": "CWE-89",
                    "description": "Динамическое выполнение SQL запросов"
                }
            ],
            "xss": [
                {
                    "pattern": r"(innerHTML\s*=\s*.*?\+.*?)",
                    "severity": "medium",
                    "cwe": "CWE-79",
                    "description": "Потенциальная XSS через innerHTML"
                },
                {
                    "pattern": r"(document\.write\s*\(.*?\+.*?\))",
                    "severity": "medium",
                    "cwe": "CWE-79", 
                    "description": "Небезопасное использование document.write"
                }
            ],
            "path_traversal": [
                {
                    "pattern": r"(\.\.\/|\.\.\\)",
                    "severity": "medium",
                    "cwe": "CWE-22",
                    "description": "Потенциальная уязвимость path traversal"
                }
            ],
            "hardcoded_secrets": [
                {
                    "pattern": r"(password\s*=\s*['\"][^'\"]{6,}['\"])",
                    "severity": "high",
                    "cwe": "CWE-798",
                    "description": "Hardcoded пароль в коде"
                },
                {
                    "pattern": r"(api_key\s*=\s*['\"][^'\"]{10,}['\"])",
                    "severity": "high",
                    "cwe": "CWE-798",
                    "description": "Hardcoded API ключ"
                }
            ],
            "weak_crypto": [
                {
                    "pattern": r"(md5|sha1)\.new\(",
                    "severity": "medium",
                    "cwe": "CWE-327",
                    "description": "Использование слабой криптографической функции"
                }
            ]
        }
    
    def _load_password_patterns(self) -> Dict[str, int]:
        """Загрузка паттернов для анализа паролей"""
        return {
            "common_passwords": [
                "password", "123456", "password123", "admin", "qwerty",
                "letmein", "welcome", "monkey", "dragon", "master"
            ],
            "keyboard_patterns": [
                "qwerty", "asdf", "zxcv", "1234", "abcd"
            ]
        }
    
    def _load_hash_signatures(self) -> Dict[int, List[str]]:
        """Загрузка сигнатур хешей по длине"""
        return {
            32: ["MD5", "NTLM"],
            40: ["SHA1", "MySQL"],
            56: ["SHA224"],
            64: ["SHA256", "Blake2s"],
            96: ["SHA384"],
            128: ["SHA512", "Blake2b", "Whirlpool"]
        }
    
    async def scan_code_vulnerabilities(self, 
                                      code: str = None,
                                      file_path: str = None,
                                      language: str = "auto") -> ToolResult:
        """Сканирование кода на уязвимости"""
        try:
            if not code and not file_path:
                return ToolResult(
                    success=False,
                    error="Необходимо указать код или путь к файлу"
                )
            
            # Читаем код из файла если нужно
            if file_path:
                path = Path(file_path)
                if not path.exists():
                    return ToolResult(
                        success=False,
                        error=f"Файл не найден: {file_path}"
                    )
                
                if path.stat().st_size > self._max_file_size:
                    return ToolResult(
                        success=False,
                        error=f"Файл слишком большой: {path.stat().st_size} байт"
                    )
                
                code = path.read_text(encoding='utf-8')
            
            # Автоопределение языка
            if language == "auto":
                language = self._detect_language(code, file_path)
            
            vulnerabilities = []
            scan_start = time.time()
            
            # Сканируем по каждой категории уязвимостей
            for category, patterns in self._vulnerability_patterns.items():
                for pattern_data in patterns:
                    pattern = pattern_data["pattern"]
                    matches = re.finditer(pattern, code, re.IGNORECASE | re.MULTILINE)
                    
                    for match in matches:
                        # Находим номер строки
                        line_num = code[:match.start()].count('\n') + 1
                        
                        vulnerability = SecurityVulnerability(
                            id=f"{category}_{len(vulnerabilities) + 1}",
                            title=f"{category.replace('_', ' ').title()} Vulnerability",
                            description=pattern_data["description"],
                            severity=pattern_data["severity"],
                            category=category,
                            location=f"Line {line_num}" + (f" in {file_path}" if file_path else ""),
                            code_snippet=match.group(0),
                            cwe_id=pattern_data.get("cwe"),
                            recommendation=self._get_vulnerability_recommendation(category)
                        )
                        vulnerabilities.append(vulnerability)
            
            scan_duration = time.time() - scan_start
            
            # Вычисляем общий рейтинг безопасности
            security_score = self._calculate_security_score(vulnerabilities, len(code.split('\n')))
            risk_level = self._get_risk_level(vulnerabilities)
            
            audit = SecurityAudit(
                target=file_path or "code_snippet",
                scan_type="static_code_analysis",
                vulnerabilities=vulnerabilities,
                security_score=security_score,
                risk_level=risk_level,
                scan_duration=scan_duration,
                recommendations=self._generate_code_recommendations(vulnerabilities),
                compliance_checks=self._check_code_compliance(code)
            )
            
            return ToolResult(
                success=True,
                data={
                    "audit": asdict(audit),
                    "summary": {
                        "total_vulnerabilities": len(vulnerabilities),
                        "critical": len([v for v in vulnerabilities if v.severity == "critical"]),
                        "high": len([v for v in vulnerabilities if v.severity == "high"]),
                        "medium": len([v for v in vulnerabilities if v.severity == "medium"]),
                        "low": len([v for v in vulnerabilities if v.severity == "low"])
                    }
                }
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Ошибка сканирования кода: {str(e)}"
            )
    
    async def analyze_password(self, password: str) -> ToolResult:
        """Анализ пароля на безопасность"""
        try:
            analysis_start = time.time()
            
            # Базовые проверки
            length = len(password)
            has_lowercase = bool(re.search(r'[a-z]', password))
            has_uppercase = bool(re.search(r'[A-Z]', password))
            has_digits = bool(re.search(r'\d', password))
            has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))
            
            # Вычисляем энтропию
            entropy = self._calculate_password_entropy(password)
            
            # Вычисляем оценку силы
            score = self._calculate_password_score(
                length, has_lowercase, has_uppercase, 
                has_digits, has_special, entropy, password
            )
            
            # Определяем уровень силы
            if score >= 90:
                strength = "very_strong"
            elif score >= 70:
                strength = "strong"
            elif score >= 50:
                strength = "medium"
            elif score >= 30:
                strength = "weak"
            else:
                strength = "very_weak"
            
            # Оценка времени взлома
            crack_time = self._estimate_crack_time(entropy)
            
            # Генерируем рекомендации
            suggestions = self._generate_password_suggestions(
                length, has_lowercase, has_uppercase, 
                has_digits, has_special, password
            )
            
            analysis = PasswordAnalysis(
                password="*" * len(password),  # Маскируем пароль
                strength=strength,
                score=score,
                length=length,
                has_lowercase=has_lowercase,
                has_uppercase=has_uppercase,
                has_digits=has_digits,
                has_special=has_special,
                entropy=entropy,
                estimated_crack_time=crack_time,
                suggestions=suggestions
            )
            
            return ToolResult(
                success=True,
                data=asdict(analysis)
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Ошибка анализа пароля: {str(e)}"
            )
    
    async def generate_secure_password(self, 
                                     length: int = 16,
                                     include_uppercase: bool = True,
                                     include_lowercase: bool = True,
                                     include_digits: bool = True,
                                     include_special: bool = True,
                                     exclude_ambiguous: bool = True) -> ToolResult:
        """Генерация безопасного пароля"""
        try:
            if length < 8:
                return ToolResult(
                    success=False,
                    error="Длина пароля должна быть не менее 8 символов"
                )
            
            # Формируем алфавит
            charset = ""
            if include_lowercase:
                charset += "abcdefghijklmnopqrstuvwxyz"
            if include_uppercase:
                charset += "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            if include_digits:
                charset += "0123456789"
            if include_special:
                charset += "!@#$%^&*()_+-=[]{}|;:,.<>?"
            
            # Исключаем неоднозначные символы
            if exclude_ambiguous:
                ambiguous = "il1Lo0O"
                charset = "".join(c for c in charset if c not in ambiguous)
            
            if not charset:
                return ToolResult(
                    success=False,
                    error="Недостаточно символов для генерации пароля"
                )
            
            # Генерируем пароль
            password = ''.join(secrets.choice(charset) for _ in range(length))
            
            # Анализируем сгенерированный пароль
            analysis_result = await self.analyze_password(password)
            
            return ToolResult(
                success=True,
                data={
                    "password": password,
                    "charset_size": len(charset),
                    "total_combinations": len(charset) ** length,
                    "analysis": analysis_result.data if analysis_result.success else None,
                    "generation_method": "cryptographically_secure"
                }
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Ошибка генерации пароля: {str(e)}"
            )
    
    async def analyze_hash(self, hash_value: str) -> ToolResult:
        """Анализ хеша"""
        try:
            hash_value = hash_value.strip()
            hash_length = len(hash_value)
            
            # Определяем возможные алгоритмы по длине
            possible_algorithms = self._hash_signatures.get(hash_length, ["Unknown"])
            
            # Анализируем формат
            format_type = "hex"
            if re.match(r'^[a-fA-F0-9]+$', hash_value):
                format_type = "hex"
            elif re.match(r'^[A-Za-z0-9+/=]+$', hash_value):
                format_type = "base64"
            else:
                format_type = "unknown"
            
            # Проверяем на наличие соли
            is_salted = self._detect_salt(hash_value)
            
            # Вычисляем уверенность в определении
            confidence = self._calculate_hash_confidence(hash_value, possible_algorithms)
            
            analysis = HashAnalysis(
                hash_value=hash_value[:32] + "..." if len(hash_value) > 32 else hash_value,
                possible_algorithms=possible_algorithms,
                hash_length=hash_length,
                format_type=format_type,
                is_salted=is_salted,
                confidence=confidence
            )
            
            return ToolResult(
                success=True,
                data=asdict(analysis)
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Ошибка анализа хеша: {str(e)}"
            )
    
    # Вспомогательные методы
    def _detect_language(self, code: str, file_path: str = None) -> str:
        """Определение языка программирования"""
        if file_path:
            ext = Path(file_path).suffix.lower()
            lang_map = {
                '.py': 'python',
                '.js': 'javascript', 
                '.php': 'php',
                '.java': 'java',
                '.cpp': 'cpp',
                '.c': 'c',
                '.cs': 'csharp',
                '.rb': 'ruby',
                '.go': 'go'
            }
            if ext in lang_map:
                return lang_map[ext]
        
        # Анализ по содержимому
        if 'def ' in code and 'import ' in code:
            return 'python'
        elif 'function' in code and ('var ' in code or 'let ' in code):
            return 'javascript'
        elif '<?php' in code:
            return 'php'
        elif 'public class' in code and 'public static void main' in code:
            return 'java'
        
        return 'unknown'
    
    def _get_vulnerability_recommendation(self, category: str) -> str:
        """Получение рекомендации для типа уязвимости"""
        recommendations = {
            "sql_injection": "Используйте параметризованные запросы или ORM",
            "xss": "Экранируйте пользовательский ввод и используйте CSP заголовки",
            "path_traversal": "Валидируйте пути файлов и используйте whitelist",
            "hardcoded_secrets": "Используйте переменные окружения или системы управления секретами",
            "weak_crypto": "Используйте современные криптографические алгоритмы (SHA-256+)"
        }
        return recommendations.get(category, "Проконсультируйтесь с экспертом по безопасности")
    
    def _calculate_security_score(self, vulnerabilities: List[SecurityVulnerability], lines_count: int) -> int:
        """Вычисление общего рейтинга безопасности"""
        if not vulnerabilities:
            return 100
        
        # Весовые коэффициенты для серьёзности
        severity_weights = {
            "critical": 40,
            "high": 25,
            "medium": 15,
            "low": 5,
            "info": 1
        }
        
        total_penalty = 0
        for vuln in vulnerabilities:
            penalty = severity_weights.get(vuln.severity, 10)
            total_penalty += penalty
        
        # Нормализация по количеству строк
        normalized_penalty = total_penalty / max(lines_count / 100, 1)
        
        score = max(0, 100 - normalized_penalty)
        return int(score)
    
    def _get_risk_level(self, vulnerabilities: List[SecurityVulnerability]) -> str:
        """Определение уровня риска"""
        critical_count = len([v for v in vulnerabilities if v.severity == "critical"])
        high_count = len([v for v in vulnerabilities if v.severity == "high"])
        
        if critical_count > 0:
            return "critical"
        elif high_count >= 3:
            return "high"
        elif high_count > 0 or len(vulnerabilities) >= 5:
            return "medium"
        else:
            return "low"
    
    def _generate_code_recommendations(self, vulnerabilities: List[SecurityVulnerability]) -> List[str]:
        """Генерация рекомендаций по коду"""
        recommendations = []
        categories = set(v.category for v in vulnerabilities)
        
        for category in categories:
            recommendations.append(self._get_vulnerability_recommendation(category))
        
        # Общие рекомендации
        if vulnerabilities:
            recommendations.extend([
                "Проведите регулярный аудит безопасности кода",
                "Используйте статические анализаторы безопасности",
                "Обучите команду разработки принципам безопасной разработки"
            ])
        
        return recommendations
    
    def _check_code_compliance(self, code: str) -> Dict[str, bool]:
        """Проверка соответствия стандартам безопасности"""
        return {
            "has_input_validation": "validate" in code.lower() or "sanitize" in code.lower(),
            "has_error_handling": "try:" in code or "catch" in code or "except" in code,
            "has_logging": "log" in code.lower() or "logger" in code.lower(),
            "no_hardcoded_secrets": not bool(re.search(r'password\s*=\s*[\'"][^\'"]{6,}[\'"]', code, re.IGNORECASE)),
            "uses_https": "https://" in code,
            "has_authentication": "auth" in code.lower() or "login" in code.lower()
        }
    
    def _calculate_password_entropy(self, password: str) -> float:
        """Вычисление энтропии пароля"""
        charset_size = 0
        
        if re.search(r'[a-z]', password):
            charset_size += 26
        if re.search(r'[A-Z]', password):
            charset_size += 26
        if re.search(r'\d', password):
            charset_size += 10
        if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            charset_size += 32
        
        if charset_size == 0:
            return 0.0
        
        import math
        return len(password) * math.log2(charset_size)
    
    def _calculate_password_score(self, length: int, has_lower: bool, has_upper: bool, 
                                has_digits: bool, has_special: bool, entropy: float, password: str) -> int:
        """Вычисление оценки силы пароля"""
        score = 0
        
        # Длина
        if length >= 12:
            score += 25
        elif length >= 8:
            score += 15
        elif length >= 6:
            score += 5
        
        # Разнообразие символов
        if has_lower:
            score += 10
        if has_upper:
            score += 10
        if has_digits:
            score += 10
        if has_special:
            score += 15
        
        # Энтропия
        if entropy >= 60:
            score += 20
        elif entropy >= 40:
            score += 10
        elif entropy >= 25:
            score += 5
        
        # Штрафы
        common_passwords = self._password_patterns["common_passwords"]
        if password.lower() in common_passwords:
            score -= 30
        
        # Проверка на клавиатурные паттерны
        keyboard_patterns = self._password_patterns["keyboard_patterns"]
        for pattern in keyboard_patterns:
            if pattern in password.lower():
                score -= 10
        
        # Проверка на повторения
        if len(set(password)) < len(password) * 0.7:
            score -= 10
        
        return max(0, min(100, score))
    
    def _estimate_crack_time(self, entropy: float) -> str:
        """Оценка времени взлома по энтропии"""
        if entropy < 20:
            return "Мгновенно"
        elif entropy < 30:
            return "Несколько секунд"
        elif entropy < 40:
            return "Несколько минут"
        elif entropy < 50:
            return "Несколько часов"
        elif entropy < 60:
            return "Несколько дней"
        elif entropy < 70:
            return "Несколько лет"
        else:
            return "Столетия"
    
    def _generate_password_suggestions(self, length: int, has_lower: bool, has_upper: bool,
                                     has_digits: bool, has_special: bool, password: str) -> List[str]:
        """Генерация рекомендаций для пароля"""
        suggestions = []
        
        if length < 12:
            suggestions.append("Увеличьте длину пароля до 12+ символов")
        
        if not has_lower:
            suggestions.append("Добавьте строчные буквы")
        if not has_upper:
            suggestions.append("Добавьте заглавные буквы")
        if not has_digits:
            suggestions.append("Добавьте цифры")
        if not has_special:
            suggestions.append("Добавьте специальные символы (!@#$%^&*)")
        
        # Проверка на общие пароли
        if password.lower() in self._password_patterns["common_passwords"]:
            suggestions.append("Не используйте распространённые пароли")
        
        # Проверка на повторения
        if len(set(password)) < len(password) * 0.7:
            suggestions.append("Избегайте повторяющихся символов")
        
        if not suggestions:
            suggestions.append("Пароль хорошего качества")
        
        return suggestions
    
    def _detect_salt(self, hash_value: str) -> bool:
        """Определение наличия соли в хеше"""
        # Простая эвристика - ищем разделители или необычную длину
        separators = ['$', ':', '.', '_']
        for sep in separators:
            if sep in hash_value:
                return True
        
        # Проверяем необычную длину для известных алгоритмов
        standard_lengths = [32, 40, 56, 64, 96, 128]
        return len(hash_value) not in standard_lengths
    
    def _calculate_hash_confidence(self, hash_value: str, algorithms: List[str]) -> float:
        """Вычисление уверенности в определении алгоритма"""
        if "Unknown" in algorithms:
            return 0.1
        
        confidence = 0.5  # базовая уверенность
        
        # Увеличиваем уверенность если формат правильный
        if re.match(r'^[a-fA-F0-9]+$', hash_value):
            confidence += 0.3
        
        # Уменьшаем если много возможных алгоритмов
        if len(algorithms) > 2:
            confidence -= 0.2
        
        return max(0.1, min(1.0, confidence))
    
    # Реализуем обязательные методы
    async def execute(self, action: str, **kwargs) -> ToolResult:
        """Выполнение действия"""
        if action == "scan_code_vulnerabilities":
            return await self.scan_code_vulnerabilities(**kwargs)
        elif action == "analyze_password":
            return await self.analyze_password(**kwargs)
        elif action == "generate_secure_password":
            return await self.generate_secure_password(**kwargs)
        elif action == "analyze_hash":
            return await self.analyze_hash(**kwargs)
        else:
            return ToolResult(
                success=False,
                error=f"Неизвестное действие: {action}"
            )
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": self.get_available_actions(),
                    "description": "Действие для выполнения"
                },
                "code": {
                    "type": "string",
                    "description": "Код для анализа уязвимостей"
                },
                "file_path": {
                    "type": "string",
                    "description": "Путь к файлу для анализа"
                },
                "language": {
                    "type": "string",
                    "description": "Язык программирования (auto для автоопределения)"
                },
                "password": {
                    "type": "string",
                    "description": "Пароль для анализа"
                },
                "hash_value": {
                    "type": "string",
                    "description": "Хеш для анализа"
                },
                "length": {
                    "type": "integer",
                    "description": "Длина генерируемого пароля"
                },
                "include_uppercase": {
                    "type": "boolean",
                    "description": "Включать заглавные буквы"
                },
                "include_lowercase": {
                    "type": "boolean", 
                    "description": "Включать строчные буквы"
                },
                "include_digits": {
                    "type": "boolean",
                    "description": "Включать цифры"
                },
                "include_special": {
                    "type": "boolean",
                    "description": "Включать специальные символы"
                },
                "exclude_ambiguous": {
                    "type": "boolean",
                    "description": "Исключать неоднозначные символы"
                }
            },
            "required": ["action"]
        } 