#!/usr/bin/env python3
"""
⚡ Быстрый тест SmartValidator на реальном файле
"""

import asyncio
from agents.smart_validator import SmartValidator


async def test_real_file():
    """Тестируем реальный файл созданный системой"""
    
    print("⚡ ТЕСТ SmartValidator НА РЕАЛЬНОМ ФАЙЛЕ")
    print("=" * 50)
    print("Файл: real_test_validator.py (создан системой)")
    print("Исходная задача: НЕИЗВЕСТНА (пусть угадает!)")
    print()
    
    validator = SmartValidator()
    
    # Тестируем без указания исходной задачи
    result = await validator.validate_result(
        original_task="",  # Пустая - заставляем угадывать!
        result={"success": True, "message": "Задача выполнена"},
        created_files=["real_test_validator.py"]
    )
    
    print("🔮 РЕЗУЛЬТАТ УМНОЙ ВАЛИДАЦИИ:")
    print(f"📊 Оценка: {result.score:.1f}/1.0")
    print(f"🎯 Вердикт: {result.verdict}")
    print(f"💰 Польза: {result.user_benefit}")
    
    if result.issues:
        print("\n⚠️  Проблемы:")
        for issue in result.issues:
            print(f"   • {issue}")
    
    if result.recommendations:
        print("\n💡 Рекомендации:")
        for rec in result.recommendations:
            print(f"   • {rec}")
    
    status = "✅ ВАЛИДНО" if result.is_valid else "❌ НЕ ВАЛИДНО"
    print(f"\n🎯 ИТОГ: {status}")
    print("\n🚀 SmartValidator успешно работает без знания исходной задачи!")


if __name__ == "__main__":
    asyncio.run(test_real_file()) 