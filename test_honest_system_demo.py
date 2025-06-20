#!/usr/bin/env python3
"""
🛡️ ДЕМОНСТРАЦИЯ СИСТЕМЫ ЧЕСТНОГО ТЕСТИРОВАНИЯ KITTYCORE 3.0

Цель: Показать как система честного тестирования решает порочный круг подделок
Принцип: "Детектор + Интегратор = Конец подделкам!"
"""

import os
import sys
import json
from pathlib import Path

# Добавляем путь к kittycore
sys.path.insert(0, str(Path(__file__).parent / 'kittycore'))

from kittycore.core.fake_detector import FakeDetector, FakeIndicator

class HonestSystemDemo:
    """Демонстрация честной системы тестирования"""
    
    def __init__(self):
        self.detector = FakeDetector()
        self.honest_tools = set()
        self.dishonest_tools = set()
        
    def test_tool_honestly(self, tool_name: str, action: str, result_data: str, has_side_effects: bool = False):
        """Честное тестирование инструмента"""
        # Создаём результат
        mock_result = type('Result', (), {
            'success': True,
            'data': result_data
        })()
        
        # Детектим подделки
        is_fake, indicators = self.detector.detect_fake_result(tool_name, action, mock_result)
        honesty_score = self.detector.get_honesty_score(indicators)
        
        # Определяем статус
        if honesty_score >= 0.7:
            status = "✅ ЧЕСТНЫЙ"
            self.honest_tools.add(tool_name)
        elif honesty_score >= 0.3:
            status = "⚠️ ПОДОЗРИТЕЛЬНЫЙ"
        else:
            status = "❌ НЕЧЕСТНЫЙ"
            self.dishonest_tools.add(tool_name)
        
        print(f"🧪 {tool_name}.{action}: {status} (честность: {honesty_score:.2f})")
        
        # Показываем найденные проблемы
        if indicators:
            for indicator in indicators[:2]:  # Показываем первые 2
                severity_emoji = {
                    "critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🔵"
                }.get(indicator.severity, "⚪")
                print(f"   {severity_emoji} {indicator.description}")
        
        return honesty_score, indicators
    
    def run_comprehensive_honesty_test(self):
        """Запуск comprehensive честного теста"""
        print("🛡️ ДЕМОНСТРАЦИЯ СИСТЕМЫ ЧЕСТНОГО ТЕСТИРОВАНИЯ")
        print("=" * 60)
        print("Цель: Автоматически обнаруживать фиктивные результаты инструментов")
        print()
        
        # 1. Тест заведомо честного инструмента
        print("📋 КАТЕГОРИЯ 1: ЧЕСТНЫЕ ИНСТРУМЕНТЫ")
        print("-" * 40)
        
        self.test_tool_honestly(
            'media_tool', 'analyze_file', 
            '{"width": 1920, "height": 1080, "format": "PNG", "file_size": 2048576, "path": "/tmp/image.png"}'
        )
        
        self.test_tool_honestly(
            'network_tool', 'ping',
            'PING google.com (142.250.185.78): 56 data bytes, 64 bytes from 142.250.185.78: icmp_seq=0 ttl=118 time=15.234 ms'
        )
        
        # 2. Тест заведомо нечестных инструментов
        print("\n📋 КАТЕГОРИЯ 2: НЕЧЕСТНЫЕ ИНСТРУМЕНТЫ")
        print("-" * 40)
        
        self.test_tool_honestly(
            'email_tool', 'send_email',
            'Email sent successfully to example@demo.com'
        )
        
        self.test_tool_honestly(
            'image_generation_tool', 'generate_image',
            'Image generated successfully: example_image.png'
        )
        
        self.test_tool_honestly(
            'telegram_tool', 'send_message',
            'Message sent to demo channel'
        )
        
        # 3. Тест подозрительных инструментов
        print("\n📋 КАТЕГОРИЯ 3: ПОДОЗРИТЕЛЬНЫЕ ИНСТРУМЕНТЫ")
        print("-" * 40)
        
        self.test_tool_honestly(
            'api_request_tool', 'get',
            'OK'
        )
        
        self.test_tool_honestly(
            'super_system_tool', 'run_command',
            'Command executed'
        )
        
        # 4. Результаты
        print("\n📊 ИТОГОВЫЕ РЕЗУЛЬТАТЫ")
        print("=" * 40)
        
        total_tools = len(self.honest_tools) + len(self.dishonest_tools)
        honest_percentage = len(self.honest_tools) / total_tools * 100 if total_tools > 0 else 0
        
        print(f"🏆 Честные инструменты ({len(self.honest_tools)}):")
        for tool in sorted(self.honest_tools):
            print(f"   ✅ {tool}")
        
        print(f"\n🚫 Нечестные инструменты ({len(self.dishonest_tools)}):")
        for tool in sorted(self.dishonest_tools):
            print(f"   ❌ {tool}")
        
        print(f"\n📈 ЧЕСТНОСТЬ СИСТЕМЫ: {honest_percentage:.1f}%")
        
        if honest_percentage < 50:
            print("🚨 КРИТИЧЕСКАЯ ПРОБЛЕМА: Большинство инструментов нечестные!")
            print("💡 РЕКОМЕНДАЦИЯ: Исправить нечестные инструменты перед продакшеном")
        elif honest_percentage < 80:
            print("⚠️ ВНИМАНИЕ: Есть нечестные инструменты, требуется доработка")
        else:
            print("🎉 ОТЛИЧНО: Система преимущественно честная!")
        
        return {
            'honest_tools': list(self.honest_tools),
            'dishonest_tools': list(self.dishonest_tools),
            'honesty_percentage': honest_percentage
        }

def main():
    """Главная демонстрация"""
    demo = HonestSystemDemo()
    
    # Запускаем comprehensive тест
    results = demo.run_comprehensive_honesty_test()
    
    # Сохраняем результаты
    with open('honest_system_demo_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Результаты сохранены в honest_system_demo_results.json")
    
    # Демонстрируем преимущества
    print("\n🚀 ПРЕИМУЩЕСТВА СИСТЕМЫ ЧЕСТНОГО ТЕСТИРОВАНИЯ:")
    print("✅ Автоматическое обнаружение подделок")
    print("✅ Честная оценка реальной функциональности")
    print("✅ Белый и чёрный списки инструментов")
    print("✅ Конец порочному кругу фиктивных тестов!")
    
    print("\n🎯 ПРИНЦИП: 'ЛУЧШЕ ЧЕСТНЫЕ 20%, ЧЕМ ФИКТИВНЫЕ 94%!'")

if __name__ == "__main__":
    main() 