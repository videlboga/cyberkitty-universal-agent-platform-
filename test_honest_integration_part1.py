#!/usr/bin/env python3
"""
🛡️ ИНТЕГРАЦИЯ СИСТЕМЫ ЧЕСТНОГО ТЕСТИРОВАНИЯ - ЧАСТЬ 1
🎯 Базовая структура честного тестирования инструментов KittyCore 3.0

ПРИНЦИПЫ:
- ❌ НЕТ МОКОВ - только реальные API вызовы
- 🕵️ АВТОМАТИЧЕСКОЕ ОБНАРУЖЕНИЕ ПОДДЕЛОК
- ✅ ЧЕСТНАЯ ОЦЕНКА ФУНКЦИОНАЛЬНОСТИ
- 📊 ДЕТАЛЬНАЯ ОТЧЁТНОСТЬ О ЧЕСТНОСТИ

ЦЕЛЬ: Заменить фиктивные тесты честными тестами раз и навсегда!
"""

import asyncio
import json
import time
import sys
import os
from pathlib import Path
from typing import Dict, List, Any, Tuple
import logging

# Добавляем путь к KittyCore
sys.path.insert(0, str(Path(__file__).parent / 'kittycore'))

from kittycore.core.fake_detector import FakeDetector, FakeIndicator

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HonestToolsTester:
    """
    🛡️ Честный тестер инструментов с автоматическим обнаружением подделок
    
    Основные возможности:
    - Интеграция FakeDetector в каждый тест
    - Автоматическая оценка честности результатов
    - Создание белого/чёрного списков инструментов
    - Детальная отчётность о проблемах
    """
    
    def __init__(self, honesty_threshold: float = 0.7):
        self.fake_detector = FakeDetector()
        self.honesty_threshold = honesty_threshold
        
        # Результаты тестирования
        self.test_results = []
        self.honest_tools = set()
        self.dishonest_tools = set()
        self.suspicious_tools = set()
        
        # Память для правильных параметров
        self.memory_records = []
        
        logger.info(f"🛡️ HonestToolsTester инициализирован (порог честности: {honesty_threshold})")
    
    def wrap_test_with_honesty_check(self, tool_name: str, action: str, test_func, *args, **kwargs):
        """
        Оборачивает любой тест проверкой на честность
        
        Args:
            tool_name: Название инструмента
            action: Действие тестирования  
            test_func: Функция теста
            *args, **kwargs: Параметры теста
            
        Returns:
            Словарь с результатами честного теста
        """
        start_time = time.time()
        
        print(f"🧪 Тестирую {tool_name}.{action} с проверкой честности...")
        
        try:
            # Выполняем оригинальный тест
            if asyncio.iscoroutinefunction(test_func):
                original_result = asyncio.run(test_func(*args, **kwargs))
            else:
                original_result = test_func(*args, **kwargs)
            
            execution_time = time.time() - start_time
            
            # Детектим подделки
            is_fake, indicators = self.fake_detector.detect_fake_result(
                tool_name, action, original_result
            )
            
            # Вычисляем оценку честности
            honesty_score = self.fake_detector.get_honesty_score(indicators)
            
            # Определяем статус честности
            honesty_status = self._determine_honesty_status(honesty_score)
            
            # Создаём честный результат
            honest_result = {
                'tool_name': tool_name,
                'action': action,
                'execution_time': execution_time,
                'original_success': getattr(original_result, 'success', False),
                'honest_success': honesty_score >= self.honesty_threshold,
                'honesty_score': honesty_score,
                'honesty_status': honesty_status,
                'is_fake': is_fake,
                'fake_indicators_count': len(indicators),
                'fake_indicators': [
                    {
                        'type': ind.type,
                        'severity': ind.severity,
                        'description': ind.description,
                        'confidence': ind.confidence
                    } for ind in indicators
                ],
                'data_size': len(str(getattr(original_result, 'data', ''))),
                'original_data_preview': str(original_result)[:200] + '...' if len(str(original_result)) > 200 else str(original_result)
            }
            
            # Обновляем статистику
            self._update_tool_statistics(tool_name, honesty_status)
            
            # Сохраняем результат
            self.test_results.append(honest_result)
            
            # Выводим результат
            self._print_test_result(honest_result, indicators)
            
            return honest_result
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_result = {
                'tool_name': tool_name,
                'action': action,
                'execution_time': execution_time,
                'original_success': False,
                'honest_success': False,
                'honesty_score': 0.0,
                'honesty_status': 'ОШИБКА',
                'is_fake': True,
                'fake_indicators_count': 0,
                'fake_indicators': [],
                'data_size': 0,
                'error': str(e),
                'original_data_preview': f"Ошибка: {str(e)}"
            }
            
            self.dishonest_tools.add(tool_name)
            self.test_results.append(error_result)
            
            print(f"   ❌ ОШИБКА: {str(e)[:100]}")
            return error_result
    
    def _determine_honesty_status(self, honesty_score: float) -> str:
        """Определение статуса честности по оценке"""
        if honesty_score >= self.honesty_threshold:
            return "ЧЕСТНЫЙ"
        elif honesty_score >= 0.3:
            return "ПОДОЗРИТЕЛЬНЫЙ"
        else:
            return "НЕЧЕСТНЫЙ"
    
    def _update_tool_statistics(self, tool_name: str, honesty_status: str):
        """Обновление статистики инструментов"""
        if honesty_status == "ЧЕСТНЫЙ":
            self.honest_tools.add(tool_name)
            self.dishonest_tools.discard(tool_name)
            self.suspicious_tools.discard(tool_name)
        elif honesty_status == "ПОДОЗРИТЕЛЬНЫЙ":
            self.suspicious_tools.add(tool_name)
        else:
            self.dishonest_tools.add(tool_name)
            self.honest_tools.discard(tool_name)
            self.suspicious_tools.discard(tool_name)
    
    def _print_test_result(self, result: Dict[str, Any], indicators: List[FakeIndicator]):
        """Красивый вывод результата теста"""
        status_emoji = {
            "ЧЕСТНЫЙ": "✅",
            "ПОДОЗРИТЕЛЬНЫЙ": "⚠️", 
            "НЕЧЕСТНЫЙ": "❌",
            "ОШИБКА": "💥"
        }.get(result['honesty_status'], "❓")
        
        print(f"   {status_emoji} {result['honesty_status']} (честность: {result['honesty_score']:.2f})")
        print(f"   📊 Время: {result['execution_time']:.1f}с, размер: {result['data_size']} байт")
        
        # Показываем первые 2 индикатора подделки
        if indicators:
            print(f"   🚨 Найдено индикаторов подделки: {len(indicators)}")
            for indicator in indicators[:2]:
                severity_emoji = {
                    "critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🔵"
                }.get(indicator.severity, "⚪")
                print(f"      {severity_emoji} {indicator.description}")
    
    def record_successful_params(self, tool_name: str, action: str, params: Dict[str, Any], notes: str = ""):
        """Записывает успешные параметры в память для будущего использования"""
        self.memory_records.append({
            "tool": tool_name,
            "working_action": action,
            "correct_params": params,
            "notes": notes,
            "timestamp": time.time()
        })
    
    def generate_honesty_summary(self) -> str:
        """Генерация итогового отчёта о честности"""
        if not self.test_results:
            return "📝 Нет результатов тестирования"
        
        total_tests = len(self.test_results)
        honest_count = len([r for r in self.test_results if r['honesty_status'] == 'ЧЕСТНЫЙ'])
        dishonest_count = len([r for r in self.test_results if r['honesty_status'] == 'НЕЧЕСТНЫЙ']) 
        suspicious_count = len([r for r in self.test_results if r['honesty_status'] == 'ПОДОЗРИТЕЛЬНЫЙ'])
        error_count = len([r for r in self.test_results if r['honesty_status'] == 'ОШИБКА'])
        
        average_honesty = sum(r['honesty_score'] for r in self.test_results) / total_tests
        
        summary = [
            "🛡️ ИТОГОВЫЙ ОТЧЁТ О ЧЕСТНОСТИ ТЕСТИРОВАНИЯ",
            "=" * 50,
            f"📊 ОБЩАЯ СТАТИСТИКА:",
            f"   Всего тестов: {total_tests}",
            f"   ✅ Честных: {honest_count} ({honest_count/total_tests*100:.1f}%)",
            f"   ❌ Нечестных: {dishonest_count} ({dishonest_count/total_tests*100:.1f}%)",
            f"   ⚠️ Подозрительных: {suspicious_count} ({suspicious_count/total_tests*100:.1f}%)", 
            f"   💥 Ошибок: {error_count} ({error_count/total_tests*100:.1f}%)",
            f"   📈 Средняя честность: {average_honesty:.2f}/1.00",
            "",
            "🏆 БЕЛЫЙ СПИСОК (честные инструменты):",
        ]
        
        for tool in sorted(self.honest_tools):
            summary.append(f"   ✅ {tool}")
        
        if self.dishonest_tools:
            summary.extend([
                "",
                "🚫 ЧЁРНЫЙ СПИСОК (нечестные инструменты):",
            ])
            for tool in sorted(self.dishonest_tools):
                summary.append(f"   ❌ {tool}")
        
        if self.suspicious_tools:
            summary.extend([
                "",
                "⚠️ ПОДОЗРИТЕЛЬНЫЕ ИНСТРУМЕНТЫ:",
            ])
            for tool in sorted(self.suspicious_tools):
                summary.append(f"   ⚠️ {tool}")
        
        # Рекомендации
        summary.extend([
            "",
            "💡 РЕКОМЕНДАЦИИ:",
        ])
        
        if average_honesty < 0.5:
            summary.append("   🚨 КРИТИЧНО: Система преимущественно нечестная - требуется полная переработка!")
        elif average_honesty < 0.7:
            summary.append("   ⚠️ ВНИМАНИЕ: Много нечестных инструментов - нужны исправления")
        else:
            summary.append("   🎉 ОТЛИЧНО: Система преимущественно честная!")
        
        summary.append(f"   🎯 ПРИНЦИП: Лучше честные {average_honesty*100:.0f}%, чем фиктивные 94%!")
        
        return "\n".join(summary)
    
    def save_honesty_results(self, filepath: str = "honesty_test_results.json"):
        """Сохранение результатов честного тестирования"""
        data = {
            'test_results': self.test_results,
            'honest_tools': list(self.honest_tools),
            'dishonest_tools': list(self.dishonest_tools),
            'suspicious_tools': list(self.suspicious_tools),
            'memory_records': self.memory_records,
            'honesty_threshold': self.honesty_threshold,
            'summary_stats': {
                'total_tests': len(self.test_results),
                'honest_percentage': len(self.honest_tools) / max(1, len(self.test_results)) * 100,
                'average_honesty': sum(r['honesty_score'] for r in self.test_results) / max(1, len(self.test_results))
            },
            'generated_at': time.time()
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 Результаты честности сохранены в {filepath}")

def demo_honest_integration():
    """Демонстрация интеграции честного тестирования"""
    print("🛡️ ДЕМОНСТРАЦИЯ ИНТЕГРАЦИИ ЧЕСТНОГО ТЕСТИРОВАНИЯ - ЧАСТЬ 1")
    print("=" * 60)
    print("🎯 Цель: Показать как обернуть любой тест проверкой честности")
    print()
    
    tester = HonestToolsTester()
    
    # Симулируем несколько тестов
    def mock_honest_test():
        return type('Result', (), {'success': True, 'data': {'real_data': True, 'size': 1024}})()
    
    def mock_fake_test():
        return type('Result', (), {'success': True, 'data': 'This is example demo data'})()
    
    def mock_error_test():
        raise Exception("API key missing")
    
    # Тестируем с проверкой честности
    print("📋 ТЕСТИРОВАНИЕ С ПРОВЕРКОЙ ЧЕСТНОСТИ:")
    print("-" * 40)
    
    tester.wrap_test_with_honesty_check("media_tool", "analyze_file", mock_honest_test)
    tester.wrap_test_with_honesty_check("email_tool", "send_email", mock_fake_test)
    tester.wrap_test_with_honesty_check("broken_tool", "test_action", mock_error_test)
    
    # Показываем отчёт
    print("\n" + tester.generate_honesty_summary())
    
    # Сохраняем результаты
    tester.save_honesty_results("demo_honest_integration_results.json")
    print("\n💾 Результаты сохранены в demo_honest_integration_results.json")

if __name__ == "__main__":
    demo_honest_integration() 