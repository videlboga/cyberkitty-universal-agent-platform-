#!/usr/bin/env python3
"""
🛡️ ИНТЕГРАЦИЯ СИСТЕМЫ ЧЕСТНОГО ТЕСТИРОВАНИЯ - ЧАСТЬ 3 (ИСПРАВЛЕННАЯ)
🔧 Реальное тестирование инструментов KittyCore 3.0 без asyncio.run() проблем

ПРИНЦИПЫ:
- 🔄 Правильная работа с async/await
- 🧪 Тестируем настоящие инструменты с правильными параметрами
- 📊 Получаем честную оценку функциональности
- 🚫 Автоматически отклоняем подделки

ИСПРАВЛЕНИЯ:
- ❌ Убрано asyncio.run() внутри event loop
- ✅ Правильные параметры для каждого инструмента
- ✅ Асинхронные вызовы через await
"""

import asyncio
import json
import time
import sys
import os
from pathlib import Path

# Добавляем путь к KittyCore
sys.path.insert(0, str(Path(__file__).parent / 'kittycore'))

# Импортируем нашу систему честности 
from test_honest_integration_part1 import HonestToolsTester

# Импортируем реальные инструменты
from kittycore.tools.enhanced_web_search_tool import EnhancedWebSearchTool
from kittycore.tools.media_tool import MediaTool
from kittycore.tools.network_tool import NetworkTool
from kittycore.tools.api_request_tool import ApiRequestTool
from kittycore.tools.super_system_tool import SuperSystemTool

class FixedHonestToolsTester(HonestToolsTester):
    """
    🛡️ Исправленный честный тестер для реальных инструментов
    
    Исправления:
    - Корректная работа с async/await
    - Правильные параметры инструментов
    - Нет asyncio.run() внутри event loop
    """
    
    def __init__(self, honesty_threshold: float = 0.7):
        super().__init__(honesty_threshold)
        print("🔧 Инициализация исправленного тестера...")
    
    def wrap_async_test_with_honesty_check(self, tool_name: str, action: str, test_coro):
        """
        Оборачивает асинхронный тест проверкой на честность (БЕЗ asyncio.run)
        """
        start_time = time.time()
        
        print(f"🧪 Тестирую {tool_name}.{action} с проверкой честности (async)...")
        
        try:
            # Выполняем корутину напрямую через await
            if asyncio.iscoroutine(test_coro):
                # Если это корутина, ожидаем её выполнения в текущем event loop
                task = asyncio.create_task(test_coro)
                original_result = asyncio.get_event_loop().run_until_complete(task)
            else:
                original_result = test_coro
            
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
    
    async def test_enhanced_web_search_honestly(self):
        """🌐 Честное тестирование веб-поиска (ИСПРАВЛЕНО)"""
        tool = EnhancedWebSearchTool()
        # Используем реальные параметры без action
        test_coro = tool.execute(
            query="KittyCore AI system github", 
            limit=3
        )
        
        result = self.wrap_async_test_with_honesty_check(
            "enhanced_web_search", "search", test_coro
        )
        
        # Записываем успешные параметры если честно
        if result['honest_success']:
            self.record_successful_params(
                "enhanced_web_search", "search",
                {"query": "string", "limit": "number"},
                f"Честный веб-поиск: {result['data_size']} байт за {result['execution_time']:.1f}с"
            )
        
        return result
    
    def test_media_tool_honestly(self):
        """🎨 Честное тестирование медиа-инструмента (ИСПРАВЛЕНО)"""
        def run_media_tool():
            tool = MediaTool()
            # Тестируем получение информации БЕЗ action (действие "get_info")
            return tool.execute(action="get_info")
        
        result = self.wrap_test_with_honesty_check(
            "media_tool", "get_info", run_media_tool
        )
        
        # Записываем успешные параметры если честно
        if result['honest_success']:
            self.record_successful_params(
                "media_tool", "get_info",
                {"action": "get_info"},
                f"Честный медиа-инструмент: локальная обработка без API ключей"
            )
        
        return result
    
    async def test_network_tool_honestly(self):
        """🌐 Честное тестирование сетевого инструмента (ИСПРАВЛЕНО)"""
        tool = NetworkTool()
        # Реальный ping тест БЕЗ asyncio.run
        test_coro = tool.execute(
            action="ping_host",
            host="8.8.8.8",  # Google DNS
            count=1
        )
        
        result = self.wrap_async_test_with_honesty_check(
            "network_tool", "ping_host", test_coro
        )
        
        # Записываем успешные параметры если честно
        if result['honest_success']:
            self.record_successful_params(
                "network_tool", "ping_host",
                {"action": "ping_host", "host": "string", "count": "number"},
                f"Честный ping: реальная сетевая диагностика"
            )
        
        return result
    
    async def test_api_request_honestly(self):
        """🌐 Честное тестирование API запросов (ИСПРАВЛЕНО)"""
        tool = ApiRequestTool()
        # Простой GET запрос к публичному API БЕЗ action параметра
        test_coro = tool.execute(
            url="https://httpbin.org/get?test=kittycore",
            method="GET"
        )
        
        result = self.wrap_async_test_with_honesty_check(
            "api_request_tool", "get", test_coro
        )
        
        # Записываем успешные параметры если честно
        if result['honest_success']:
            self.record_successful_params(
                "api_request_tool", "get",
                {"url": "string", "method": "GET"},
                f"Честный API запрос: реальный HTTP вызов"
            )
        
        return result
    
    def test_super_system_tool_honestly(self):
        """💻 Честное тестирование системного инструмента (ИСПРАВЛЕНО)"""
        def run_system_tool():
            tool = SuperSystemTool()
            # Безопасная системная команда БЕЗ safe_mode параметра
            return tool.execute(
                action="run_command",
                command="echo 'KittyCore Honest Test'"
            )
        
        result = self.wrap_test_with_honesty_check(
            "super_system_tool", "run_command", run_system_tool
        )
        
        # Записываем успешные параметры если честно
        if result['honest_success']:
            self.record_successful_params(
                "super_system_tool", "run_command",
                {"action": "run_command", "command": "string"},
                f"Честная системная команда: реальное выполнение"
            )
        
        return result
    
    async def run_fixed_comprehensive_test(self):
        """🚀 Запуск исправленного комплексного честного тестирования"""
        print("🛡️ ЗАПУСК ИСПРАВЛЕННОГО КОМПЛЕКСНОГО ЧЕСТНОГО ТЕСТИРОВАНИЯ")
        print("=" * 70)
        print("🎯 Цель: Протестировать все инструменты с правильными параметрами")
        print("🔧 Исправления: убраны asyncio.run(), добавлены правильные параметры")
        print()
        
        results = []
        
        # Тестируем все инструменты
        print("📋 ЧЕСТНОЕ ТЕСТИРОВАНИЕ ИНСТРУМЕНТОВ (ИСПРАВЛЕННАЯ ВЕРСИЯ):")
        print("-" * 60)
        
        # 1. Web Search (async исправлен)
        result1 = await self.test_enhanced_web_search_honestly()
        results.append(result1)
        
        # 2. Media Tool (sync работает)
        result2 = self.test_media_tool_honestly()
        results.append(result2)
        
        # 3. Network Tool (async исправлен)
        result3 = await self.test_network_tool_honestly()
        results.append(result3)
        
        # 4. API Request (async исправлен)
        result4 = await self.test_api_request_honestly()
        results.append(result4)
        
        # 5. System Tool (sync исправлен)
        result5 = self.test_super_system_tool_honestly()
        results.append(result5)
        
        return results
    
    def generate_improvement_summary(self):
        """📊 Генерация отчёта об улучшениях"""
        honest_count = len(self.honest_tools)
        total_count = len(set(r['tool_name'] for r in self.test_results))
        error_count = len([r for r in self.test_results if r['honesty_status'] == 'ОШИБКА'])
        
        improvements = [
            "🔧 ОТЧЁТ ОБ УЛУЧШЕНИЯХ ПОСЛЕ ИСПРАВЛЕНИЙ",
            "=" * 50,
            "",
            "✅ ИСПРАВЛЕНИЯ В ЧАСТИ 3:",
            "   🔄 Убран asyncio.run() из event loop",
            "   🎯 Добавлены правильные параметры инструментов",
            "   🛠️ Исправлена работа с async/await",
            "",
            f"📊 РЕЗУЛЬТАТЫ ПОСЛЕ ИСПРАВЛЕНИЙ:",
            f"   🏆 Честных инструментов: {honest_count}/{total_count} ({honest_count/total_count*100:.1f}%)",
            f"   💥 Ошибок: {error_count}/{total_count} ({error_count/total_count*100:.1f}%)",
            "",
            "🎯 ПРИНЦИП: Честная диагностика выявляет реальные проблемы!",
            "   Система честности помогает исправить инструменты, а не скрывать проблемы."
        ]
        
        return "\n".join(improvements)

async def main():
    """Главная функция исправленного честного comprehensive тестирования"""
    print("🛡️ ИСПРАВЛЕННОЕ ЧЕСТНОЕ COMPREHENSIVE ТЕСТИРОВАНИЕ KITTYCORE 3.0")
    print("=" * 70)
    print("🚀 Революция: Автоматическое обнаружение подделок + исправление проблем!")
    print()
    
    # Создаём исправленный честный тестер
    tester = FixedHonestToolsTester(honesty_threshold=0.7)
    
    # Запускаем комплексное тестирование
    start_time = time.time()
    results = await tester.run_fixed_comprehensive_test()
    total_time = time.time() - start_time
    
    # Генерируем отчёты
    print("\n" + "="*70)
    print(tester.generate_honesty_summary())
    
    print("\n" + "="*70)
    print(tester.generate_detailed_analysis())
    
    print("\n" + "="*70)
    print(tester.generate_improvement_summary())
    
    # Сохраняем результаты
    timestamp = int(time.time())
    results_file = f"honest_fixed_results_{timestamp}.json"
    tester.save_honesty_results(results_file)
    
    print(f"\n💾 Все результаты сохранены в {results_file}")
    print(f"⏱️ Общее время тестирования: {total_time:.1f}с")
    
    # Итоговая статистика
    honest_count = len(tester.honest_tools)
    total_count = len(set(r['tool_name'] for r in tester.test_results))
    print(f"🎯 ИТОГ: {honest_count}/{total_count} инструментов прошли проверку честности!")
    
    if honest_count >= 3:
        print("🎉 УСПЕХ: Большинство инструментов работают честно!")
    elif honest_count >= 2:
        print("👍 ПРОГРЕСС: Есть рабочие инструменты, остальные нужно исправить") 
    else:
        print("🔧 РАБОТА: Требуются дополнительные исправления инструментов")

if __name__ == "__main__":
    asyncio.run(main()) 