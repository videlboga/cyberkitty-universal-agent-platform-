#!/usr/bin/env python3
"""
🕵️ ДЕТЕКТОР ПОДДЕЛОК KITTYCORE 3.0

Цель: Автоматически обнаруживать фиктивные результаты инструментов
Принцип: "Виновен в подделке, пока не докажешь обратное"

Проверяет:
- Паттерны заглушек в тексте
- Успех без необходимых API ключей
- Отсутствие побочных эффектов
- Подозрительные размеры данных
"""

import os
import re
import json
from typing import Dict, List, Tuple, Any, Optional
from pathlib import Path
import logging
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class FakeIndicator:
    """Индикатор подделки"""
    type: str  # "pattern", "missing_key", "no_side_effect", "suspicious_data"
    severity: str  # "critical", "high", "medium", "low"
    description: str
    confidence: float  # 0.0-1.0

class FakeDetector:
    """
    🕵️ Детектор подделок результатов инструментов
    
    Основные возможности:
    - Поиск паттернов заглушек
    - Проверка наличия необходимых API ключей
    - Валидация побочных эффектов
    - Анализ подозрительных данных
    """
    
    def __init__(self):
        # Паттерны заглушек
        self.fake_patterns = [
            r"\b(demo|mock|заглушка|example|placeholder|dummy|fake|test.data)\b",
            r"\b(пример|образец|шаблон|демо.режим|временно)\b",
            r"\b(coming.soon|under.development|not.implemented)\b",
            r"\b(todo|fixme|tbd|тут.будет|здесь.будет)\b"
        ]
        
        # Критические требования к API ключам
        self.api_requirements = {
            'email_tool': ['SMTP_SERVER', 'SMTP_USERNAME', 'SMTP_PASSWORD'],
            'image_generation_tool': ['REPLICATE_API_TOKEN'],
            'telegram_tool': ['TELEGRAM_API_ID', 'TELEGRAM_API_HASH'],
            'database_tool': ['DATABASE_URL'],
            'ai_integration_tool': ['OPENROUTER_API_KEY']
        }
        
        # Подозрительные размеры данных
        self.suspicious_sizes = {
            'too_small': 10,      # < 10 байт подозрительно
            'too_generic': 50,    # 10-50 байт может быть заглушкой
            'template_size': 100  # Ровно 100 байт часто шаблон
        }
        
        logger.info("🕵️ FakeDetector инициализирован")
    
    def detect_fake_result(self, tool_name: str, action: str, result: Any) -> Tuple[bool, List[FakeIndicator]]:
        """
        Главная функция детекции подделок
        
        Returns:
            (is_fake, indicators) - подделка ли результат и список индикаторов
        """
        indicators = []
        
        # 1. Проверка паттернов заглушек
        pattern_indicators = self._check_fake_patterns(result)
        indicators.extend(pattern_indicators)
        
        # 2. Проверка API ключей
        api_indicators = self._check_missing_api_keys(tool_name, result)
        indicators.extend(api_indicators)
        
        # 3. Проверка побочных эффектов
        side_effect_indicators = self._check_side_effects(tool_name, action, result)
        indicators.extend(side_effect_indicators)
        
        # 4. Проверка подозрительных данных
        data_indicators = self._check_suspicious_data(result)
        indicators.extend(data_indicators)
        
        # Определяем общий вердикт
        is_fake = self._calculate_fake_verdict(indicators)
        
        if indicators:
            logger.warning(f"🚨 Найдены индикаторы подделки для {tool_name}.{action}: {len(indicators)}")
            
        return is_fake, indicators
    
    def _check_fake_patterns(self, result: Any) -> List[FakeIndicator]:
        """Проверка паттернов заглушек в результате"""
        indicators = []
        result_text = str(result).lower()
        
        for pattern in self.fake_patterns:
            matches = re.findall(pattern, result_text, re.IGNORECASE)
            if matches:
                indicators.append(FakeIndicator(
                    type="pattern",
                    severity="high",
                    description=f"Найден паттерн заглушки: {matches}",
                    confidence=0.9
                ))
        
        return indicators
    
    def _check_missing_api_keys(self, tool_name: str, result: Any) -> List[FakeIndicator]:
        """Проверка успеха без необходимых API ключей"""
        indicators = []
        
        # Проверяем только если результат "успешный"
        result_success = getattr(result, 'success', None)
        if not result_success:
            return indicators
            
        # Проверяем наличие требуемых ключей
        required_keys = self.api_requirements.get(tool_name, [])
        for key in required_keys:
            if not os.getenv(key):
                indicators.append(FakeIndicator(
                    type="missing_key",
                    severity="critical",
                    description=f"Успех без обязательного API ключа: {key}",
                    confidence=1.0
                ))
        
        return indicators
    
    def _check_side_effects(self, tool_name: str, action: str, result: Any) -> List[FakeIndicator]:
        """Проверка наличия ожидаемых побочных эффектов"""
        indicators = []
        
        # Специфические проверки по инструментам
        if tool_name == 'email_tool' and action == 'send_email':
            if not self._check_email_side_effects(result):
                indicators.append(FakeIndicator(
                    type="no_side_effect",
                    severity="critical", 
                    description="Email отправлен без побочных эффектов",
                    confidence=0.95
                ))
                
        elif tool_name == 'super_system_tool' and 'create' in action:
            if not self._check_file_creation_side_effects(result):
                indicators.append(FakeIndicator(
                    type="no_side_effect",
                    severity="high",
                    description="Файл создан без реальных побочных эффектов",
                    confidence=0.8
                ))
        
        return indicators
    
    def _check_suspicious_data(self, result: Any) -> List[FakeIndicator]:
        """Проверка подозрительных характеристик данных"""
        indicators = []
        
        result_data = getattr(result, 'data', str(result))
        data_size = len(str(result_data))
        
        # Слишком маленький размер
        if data_size < self.suspicious_sizes['too_small']:
            indicators.append(FakeIndicator(
                type="suspicious_data",
                severity="medium",
                description=f"Подозрительно маленький размер данных: {data_size} байт",
                confidence=0.6
            ))
        
        # Подозрительно ровный размер (часто в шаблонах)
        if data_size in [50, 100, 200, 500, 1000]:
            indicators.append(FakeIndicator(
                type="suspicious_data", 
                severity="low",
                description=f"Подозрительно ровный размер: {data_size} байт",
                confidence=0.3
            ))
        
        return indicators
    
    def _check_email_side_effects(self, result: Any) -> bool:
        """Проверка побочных эффектов отправки email"""
        # Проверяем наличие SMTP логов, файлов outbox, счётчиков и т.д.
        smtp_log_exists = Path('/var/log/mail.log').exists() or Path('/tmp/kittycore_smtp.log').exists()
        outbox_exists = Path('/tmp/kittycore_outbox').exists()
        
        return smtp_log_exists or outbox_exists
    
    def _check_file_creation_side_effects(self, result: Any) -> bool:
        """Проверка побочных эффектов создания файлов"""
        # Проверяем упоминание реальных путей в результате
        result_str = str(result)
        file_patterns = [r'/tmp/', r'/home/', r'\.txt', r'\.py', r'\.html']
        
        for pattern in file_patterns:
            if re.search(pattern, result_str):
                # Дополнительно проверяем существование файла
                potential_paths = re.findall(r'(/\S+\.\w+)', result_str)
                for path in potential_paths:
                    if Path(path).exists():
                        return True
        
        return False
    
    def _calculate_fake_verdict(self, indicators: List[FakeIndicator]) -> bool:
        """Вычисление итогового вердикта о подделке"""
        if not indicators:
            return False
            
        # Критические индикаторы = автоматически подделка
        critical_indicators = [i for i in indicators if i.severity == "critical"]
        if critical_indicators:
            return True
        
        # Высчитываем общий балл подозрительности
        total_score = sum(i.confidence for i in indicators)
        high_severity_count = len([i for i in indicators if i.severity == "high"])
        
        # Подделка если:
        # - Общий балл > 1.5 ИЛИ
        # - Больше 2 индикаторов высокой важности
        return total_score > 1.5 or high_severity_count > 2
    
    def generate_fake_report(self, tool_name: str, action: str, indicators: List[FakeIndicator]) -> str:
        """Генерация отчёта о найденных подделках"""
        if not indicators:
            return f"✅ {tool_name}.{action}: Подделок не обнаружено"
        
        report = [f"🚨 ОТЧЁТ О ПОДДЕЛКАХ: {tool_name}.{action}"]
        report.append("=" * 50)
        
        for i, indicator in enumerate(indicators, 1):
            severity_emoji = {
                "critical": "🔴",
                "high": "🟠", 
                "medium": "🟡",
                "low": "🔵"
            }.get(indicator.severity, "⚪")
            
            report.append(
                f"{i}. {severity_emoji} {indicator.severity.upper()}: "
                f"{indicator.description} (доверие: {indicator.confidence:.1f})"
            )
        
        fake_verdict = self._calculate_fake_verdict(indicators)
        verdict_emoji = "❌ ПОДДЕЛКА" if fake_verdict else "⚠️ ПОДОЗРИТЕЛЬНО"
        report.append(f"\n🎯 ВЕРДИКТ: {verdict_emoji}")
        
        return "\n".join(report)
    
    def get_honesty_score(self, indicators: List[FakeIndicator]) -> float:
        """Получение оценки честности (0.0 = подделка, 1.0 = честно)"""
        if not indicators:
            return 1.0
            
        # Штрафы за индикаторы
        penalty = 0.0
        for indicator in indicators:
            severity_penalties = {
                "critical": 1.0,  # Критический = полный провал
                "high": 0.4,      # Высокий = серьёзный штраф
                "medium": 0.2,    # Средний = средний штраф
                "low": 0.1        # Низкий = лёгкий штраф
            }
            penalty += severity_penalties.get(indicator.severity, 0.1) * indicator.confidence
        
        honesty_score = max(0.0, 1.0 - penalty)
        return honesty_score

def main():
    """Пример использования детектора подделок"""
    detector = FakeDetector()
    
    # Тест 1: Явная подделка
    print("🧪 ТЕСТ 1: Явная подделка")
    fake_result_mock = type('MockResult', (), {
        'success': True,
        'data': 'This is example data for demo purposes'
    })()
    
    is_fake, indicators = detector.detect_fake_result('email_tool', 'send_email', fake_result_mock)
    print(detector.generate_fake_report('email_tool', 'send_email', indicators))
    print(f"Оценка честности: {detector.get_honesty_score(indicators):.2f}")
    
    print("\n" + "="*60 + "\n")
    
    # Тест 2: Честный результат
    print("🧪 ТЕСТ 2: Честный результат")
    honest_result = type('HonestResult', (), {
        'success': True,
        'data': {'file_size': 1024, 'path': '/tmp/real_file.txt', 'status': 'created'}
    })()
    
    is_fake2, indicators2 = detector.detect_fake_result('media_tool', 'analyze_file', honest_result)
    print(detector.generate_fake_report('media_tool', 'analyze_file', indicators2))
    print(f"Оценка честности: {detector.get_honesty_score(indicators2):.2f}")

if __name__ == "__main__":
    main() 