#!/usr/bin/env python3
"""
🛡️ ИНТЕГРАТОР ЧЕСТНОГО ТЕСТИРОВАНИЯ KITTYCORE 3.0

Цель: Интегрировать детектор подделок во все существующие тесты
Принцип: "Каждый тест автоматически проверяется на честность"

Возможности:
- Автоматическая интеграция FakeDetector
- Переписывание результатов тестов
- Создание отчётов о честности
- Блокировка нечестных инструментов
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Any, Tuple
import logging
from datetime import datetime

from kittycore.core.fake_detector import FakeDetector, FakeIndicator

logger = logging.getLogger(__name__)

class HonestTestIntegrator:
    """
    🛡️ Интегратор честного тестирования
    
    Основные возможности:
    - Интеграция детектора подделок в тесты
    - Автоматическое переписывание результатов
    - Создание белого списка честных инструментов
    - Генерация отчётов о честности
    """
    
    def __init__(self, honesty_threshold: float = 0.7):
        self.fake_detector = FakeDetector()
        self.honesty_threshold = honesty_threshold
        self.honest_tools = set()  # Белый список честных инструментов
        self.dishonest_tools = set()  # Чёрный список нечестных инструментов
        self.test_results = []  # История результатов тестов
        
        logger.info(f"🛡️ HonestTestIntegrator инициализирован (порог честности: {honesty_threshold})")
    
    def wrap_test_result(self, tool_name: str, action: str, original_result: Any) -> Dict[str, Any]:
        """
        Оборачивает результат теста проверкой на честность
        
        Returns:
            Словарь с честным анализом результата
        """
        # Детектим подделки
        is_fake, indicators = self.fake_detector.detect_fake_result(tool_name, action, original_result)
        
        # Вычисляем оценку честности
        honesty_score = self.fake_detector.get_honesty_score(indicators)
        
        # Определяем статус честности
        if honesty_score >= self.honesty_threshold:
            honesty_status = "ЧЕСТНЫЙ"
            self.honest_tools.add(tool_name)
        elif honesty_score >= 0.3:
            honesty_status = "ПОДОЗРИТЕЛЬНЫЙ"
        else:
            honesty_status = "НЕЧЕСТНЫЙ"
            self.dishonest_tools.add(tool_name)
        
        # Создаём честный результат
        honest_result = {
            'tool_name': tool_name,
            'action': action,
            'original_success': getattr(original_result, 'success', False),
            'honest_success': honesty_score >= self.honesty_threshold,
            'honesty_score': honesty_score,
            'honesty_status': honesty_status,
            'is_fake': is_fake,
            'fake_indicators': [
                {
                    'type': ind.type,
                    'severity': ind.severity, 
                    'description': ind.description,
                    'confidence': ind.confidence
                } for ind in indicators
            ],
            'data_size': len(str(getattr(original_result, 'data', ''))),
            'timestamp': datetime.now().isoformat(),
            'original_data': str(original_result)[:200] + '...' if len(str(original_result)) > 200 else str(original_result)
        }
        
        # Сохраняем в историю
        self.test_results.append(honest_result)
        
        return honest_result
    
    def generate_honesty_report(self) -> str:
        """Генерация отчёта о честности всех тестов"""
        if not self.test_results:
            return "📝 Нет результатов для анализа честности"
        
        # Статистика
        total_tests = len(self.test_results)
        honest_tests = len([r for r in self.test_results if r['honesty_status'] == 'ЧЕСТНЫЙ'])
        dishonest_tests = len([r for r in self.test_results if r['honesty_status'] == 'НЕЧЕСТНЫЙ'])
        suspicious_tests = len([r for r in self.test_results if r['honesty_status'] == 'ПОДОЗРИТЕЛЬНЫЙ'])
        
        average_honesty = sum(r['honesty_score'] for r in self.test_results) / total_tests
        
        report = [
            "🛡️ ОТЧЁТ О ЧЕСТНОСТИ ТЕСТИРОВАНИЯ KITTYCORE 3.0",
            "=" * 60,
            f"📊 ОБЩАЯ СТАТИСТИКА:",
            f"   Всего тестов: {total_tests}",
            f"   ✅ Честных: {honest_tests} ({honest_tests/total_tests*100:.1f}%)",
            f"   ❌ Нечестных: {dishonest_tests} ({dishonest_tests/total_tests*100:.1f}%)",
            f"   ⚠️ Подозрительных: {suspicious_tests} ({suspicious_tests/total_tests*100:.1f}%)",
            f"   📈 Средняя честность: {average_honesty:.2f}/1.00",
            "",
            "🏆 БЕЛЫЙ СПИСОК (честные инструменты):",
        ]
        
        for tool in sorted(self.honest_tools):
            tool_results = [r for r in self.test_results if r['tool_name'] == tool and r['honesty_status'] == 'ЧЕСТНЫЙ']
            avg_score = sum(r['honesty_score'] for r in tool_results) / len(tool_results) if tool_results else 0
            report.append(f"   ✅ {tool} (честность: {avg_score:.2f})")
        
        if self.dishonest_tools:
            report.extend([
                "",
                "🚫 ЧЁРНЫЙ СПИСОК (нечестные инструменты):",
            ])
            for tool in sorted(self.dishonest_tools):
                tool_results = [r for r in self.test_results if r['tool_name'] == tool and r['honesty_status'] == 'НЕЧЕСТНЫЙ']
                avg_score = sum(r['honesty_score'] for r in tool_results) / len(tool_results) if tool_results else 0
                report.append(f"   ❌ {tool} (честность: {avg_score:.2f})")
        
        # Детальный анализ нечестных результатов
        dishonest_results = [r for r in self.test_results if r['honesty_status'] == 'НЕЧЕСТНЫЙ']
        if dishonest_results:
            report.extend([
                "",
                "🔍 ДЕТАЛЬНЫЙ АНАЛИЗ НЕЧЕСТНЫХ РЕЗУЛЬТАТОВ:",
                "-" * 50,
            ])
            
            for result in dishonest_results[:5]:  # Показываем только первые 5
                report.append(f"❌ {result['tool_name']}.{result['action']} (честность: {result['honesty_score']:.2f})")
                for indicator in result['fake_indicators'][:3]:  # Показываем первые 3 индикатора
                    severity_emoji = {
                        "critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🔵"
                    }.get(indicator['severity'], "⚪")
                    report.append(f"   {severity_emoji} {indicator['description']}")
                report.append("")
        
        return "\n".join(report)
    
    def save_honesty_results(self, filepath: str = "honesty_results.json"):
        """Сохранение результатов честности в файл"""
        data = {
            'honest_tools': list(self.honest_tools),
            'dishonest_tools': list(self.dishonest_tools),
            'test_results': self.test_results,
            'honesty_threshold': self.honesty_threshold,
            'generated_at': datetime.now().isoformat()
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 Результаты честности сохранены в {filepath}")
    
    def load_honesty_results(self, filepath: str = "honesty_results.json"):
        """Загрузка результатов честности из файла"""
        if not Path(filepath).exists():
            logger.warning(f"📂 Файл {filepath} не найден")
            return
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.honest_tools = set(data.get('honest_tools', []))
        self.dishonest_tools = set(data.get('dishonest_tools', []))
        self.test_results = data.get('test_results', [])
        
        logger.info(f"📁 Результаты честности загружены из {filepath}")
    
    def is_tool_honest(self, tool_name: str) -> bool:
        """Проверка находится ли инструмент в белом списке"""
        return tool_name in self.honest_tools
    
    def is_tool_dishonest(self, tool_name: str) -> bool:
        """Проверка находится ли инструмент в чёрном списке"""
        return tool_name in self.dishonest_tools
    
    def get_tool_reputation(self, tool_name: str) -> Dict[str, Any]:
        """Получение репутации инструмента"""
        tool_results = [r for r in self.test_results if r['tool_name'] == tool_name]
        
        if not tool_results:
            return {
                'tool_name': tool_name,
                'status': 'НЕИЗВЕСТНЫЙ',
                'tests_count': 0,
                'average_honesty': 0.0,
                'reputation': 'Не тестировался'
            }
        
        honest_count = len([r for r in tool_results if r['honesty_status'] == 'ЧЕСТНЫЙ'])
        dishonest_count = len([r for r in tool_results if r['honesty_status'] == 'НЕЧЕСТНЫЙ'])
        average_honesty = sum(r['honesty_score'] for r in tool_results) / len(tool_results)
        
        if average_honesty >= self.honesty_threshold:
            status = 'ЧЕСТНЫЙ'
            reputation = f"✅ Надёжный ({honest_count}/{len(tool_results)} честных тестов)"
        elif average_honesty >= 0.3:
            status = 'ПОДОЗРИТЕЛЬНЫЙ'
            reputation = f"⚠️ Требует внимания (честность {average_honesty:.2f})"
        else:
            status = 'НЕЧЕСТНЫЙ'
            reputation = f"❌ Ненадёжный ({dishonest_count}/{len(tool_results)} нечестных тестов)"
        
        return {
            'tool_name': tool_name,
            'status': status,
            'tests_count': len(tool_results),
            'average_honesty': average_honesty,
            'reputation': reputation,
            'honest_tests': honest_count,
            'dishonest_tests': dishonest_count
        }

def demo_integration():
    """Демонстрация интеграции честного тестирования"""
    integrator = HonestTestIntegrator()
    
    print("🛡️ ДЕМОНСТРАЦИЯ ИНТЕГРАТОРА ЧЕСТНОГО ТЕСТИРОВАНИЯ")
    print("=" * 60)
    
    # Симулируем результаты тестов
    print("\n🧪 Симулируем тесты инструментов...")
    
    # Честный инструмент
    honest_result = type('Result', (), {'success': True, 'data': {'file_size': 1024, 'path': '/tmp/real.txt'}})()
    result1 = integrator.wrap_test_result('media_tool', 'analyze_file', honest_result)
    print(f"✅ {result1['tool_name']}: {result1['honesty_status']} (честность: {result1['honesty_score']:.2f})")
    
    # Нечестный инструмент
    fake_result = type('Result', (), {'success': True, 'data': 'This is example demo data'})()
    result2 = integrator.wrap_test_result('email_tool', 'send_email', fake_result)
    print(f"❌ {result2['tool_name']}: {result2['honesty_status']} (честность: {result2['honesty_score']:.2f})")
    
    # Подозрительный инструмент
    suspicious_result = type('Result', (), {'success': True, 'data': 'OK'})()
    result3 = integrator.wrap_test_result('network_tool', 'ping', suspicious_result)
    print(f"⚠️ {result3['tool_name']}: {result3['honesty_status']} (честность: {result3['honesty_score']:.2f})")
    
    print("\n📊 ОТЧЁТ О ЧЕСТНОСТИ:")
    print(integrator.generate_honesty_report())
    
    # Сохраняем результаты
    integrator.save_honesty_results("demo_honesty_results.json")
    print("\n💾 Результаты сохранены в demo_honesty_results.json")

if __name__ == "__main__":
    demo_integration() 