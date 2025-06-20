#!/usr/bin/env python3
"""
🛡️ ИНТЕГРАЦИЯ СИСТЕМЫ ЧЕСТНОГО ТЕСТИРОВАНИЯ - ЧАСТЬ 2  
🔧 Реальное тестирование инструментов KittyCore 3.0 с проверкой честности

ПРИНЦИПЫ:
- 🔄 Используем реальную функцию wrap_test_with_honesty_check
- 🧪 Тестируем настоящие инструменты  
- 📊 Получаем честную оценку функциональности
- 🚫 Автоматически отклоняем подделки

ЦЕЛЬ: Применить систему честности к реальным инструментам!
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

class RealHonestToolsTester(HonestToolsTester):
    """
    🛡️ Расширение честного тестера для реальных инструментов
    
    Добавляет специализированные методы тестирования для каждого инструмента
    """
    
    def __init__(self, honesty_threshold: float = 0.7):
        super().__init__(honesty_threshold)
        print("🔧 Инициализация тестера реальных инструментов...")
    
    async def test_enhanced_web_search_honestly(self):
        """🌐 Честное тестирование веб-поиска"""
        def run_web_search():
            tool = EnhancedWebSearchTool()
            # Используем реальные параметры из наших успешных тестов
            return asyncio.run(tool.execute(
                query="KittyCore AI system github", 
                limit=3
            ))
        
        result = self.wrap_test_with_honesty_check(
            "enhanced_web_search", "search", run_web_search
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
        """🎨 Честное тестирование медиа-инструмента"""
        def run_media_tool():
            tool = MediaTool()
            # Тестируем получение информации
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
        """🌐 Честное тестирование сетевого инструмента"""
        def run_network_tool():
            tool = NetworkTool()
            # Реальный ping тест
            return asyncio.run(tool.execute(
                action="ping_host",
                host="8.8.8.8",  # Google DNS
                count=1
            ))
        
        result = self.wrap_test_with_honesty_check(
            "network_tool", "ping_host", run_network_tool
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
        """🌐 Честное тестирование API запросов"""
        def run_api_request():
            tool = ApiRequestTool()
            # Простой GET запрос к публичному API
            return asyncio.run(tool.execute(
                action="get",
                url="https://httpbin.org/get",
                params={"test": "kittycore"}
            ))
        
        result = self.wrap_test_with_honesty_check(
            "api_request_tool", "get", run_api_request
        )
        
        # Записываем успешные параметры если честно
        if result['honest_success']:
            self.record_successful_params(
                "api_request_tool", "get",
                {"action": "get", "url": "string", "params": "dict"},
                f"Честный API запрос: реальный HTTP вызов"
            )
        
        return result
    
    def test_super_system_tool_honestly(self):
        """💻 Честное тестирование системного инструмента"""
        def run_system_tool():
            tool = SuperSystemTool()
            # Безопасная системная команда
            return tool.execute(
                action="run_command",
                command="echo 'KittyCore Honest Test'",
                safe_mode=True
            )
        
        result = self.wrap_test_with_honesty_check(
            "super_system_tool", "run_command", run_system_tool
        )
        
        # Записываем успешные параметры если честно
        if result['honest_success']:
            self.record_successful_params(
                "super_system_tool", "run_command",
                {"action": "run_command", "command": "string", "safe_mode": "boolean"},
                f"Честная системная команда: реальное выполнение"
            )
        
        return result
    
    async def run_honest_comprehensive_test(self):
        """🚀 Запуск комплексного честного тестирования"""
        print("🛡️ ЗАПУСК КОМПЛЕКСНОГО ЧЕСТНОГО ТЕСТИРОВАНИЯ")
        print("=" * 60)
        print("🎯 Цель: Протестировать все инструменты с автоматической проверкой честности")
        print()
        
        results = []
        
        # Тестируем все инструменты
        print("📋 ЧЕСТНОЕ ТЕСТИРОВАНИЕ ИНСТРУМЕНТОВ:")
        print("-" * 50)
        
        # 1. Web Search
        result1 = await self.test_enhanced_web_search_honestly()
        results.append(result1)
        
        # 2. Media Tool  
        result2 = self.test_media_tool_honestly()
        results.append(result2)
        
        # 3. Network Tool
        result3 = await self.test_network_tool_honestly()
        results.append(result3)
        
        # 4. API Request
        result4 = await self.test_api_request_honestly()
        results.append(result4)
        
        # 5. System Tool
        result5 = self.test_super_system_tool_honestly()
        results.append(result5)
        
        return results
    
    def generate_detailed_analysis(self):
        """📊 Генерация детального анализа результатов"""
        if not self.test_results:
            return "📝 Нет данных для анализа"
        
        analysis = [
            "🔍 ДЕТАЛЬНЫЙ АНАЛИЗ ЧЕСТНОСТИ ИНСТРУМЕНТОВ",
            "=" * 60,
            ""
        ]
        
        # Анализ по инструментам
        for tool_name in sorted(set(r['tool_name'] for r in self.test_results)):
            tool_results = [r for r in self.test_results if r['tool_name'] == tool_name]
            
            if not tool_results:
                continue
                
            result = tool_results[0]  # Берём последний результат
            
            analysis.append(f"🔧 {tool_name}:")
            analysis.append(f"   📊 Честность: {result['honesty_score']:.2f}/1.00")
            analysis.append(f"   🎯 Статус: {result['honesty_status']}")
            analysis.append(f"   ⏱️ Время: {result['execution_time']:.1f}с")
            analysis.append(f"   📦 Размер данных: {result['data_size']} байт")
            
            if result['fake_indicators']:
                analysis.append(f"   🚨 Проблемы:")
                for indicator in result['fake_indicators'][:3]:
                    severity_emoji = {
                        "critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🔵"
                    }.get(indicator['severity'], "⚪")
                    analysis.append(f"      {severity_emoji} {indicator['description']}")
            else:
                analysis.append(f"   ✅ Проблем не найдено")
            
            analysis.append("")
        
        # Общие выводы
        honest_tools = len(self.honest_tools)
        total_tools = len(set(r['tool_name'] for r in self.test_results))
        honesty_percentage = honest_tools / total_tools * 100 if total_tools > 0 else 0
        
        analysis.extend([
            "📈 ОБЩИЕ ВЫВОДЫ:",
            f"   🏆 Честных инструментов: {honest_tools}/{total_tools} ({honesty_percentage:.1f}%)",
            f"   🚫 Нечестных инструментов: {len(self.dishonest_tools)}",
            f"   ⚠️ Подозрительных инструментов: {len(self.suspicious_tools)}",
            ""
        ])
        
        if honesty_percentage >= 80:
            analysis.append("🎉 ОТЛИЧНО: Система KittyCore 3.0 преимущественно честная!")
        elif honesty_percentage >= 60:
            analysis.append("👍 ХОРОШО: Большинство инструментов работают честно")
        elif honesty_percentage >= 40:
            analysis.append("⚠️ ВНИМАНИЕ: Половина инструментов требует доработки")
        else:
            analysis.append("🚨 КРИТИЧНО: Система нуждается в серьёзных исправлениях!")
        
        analysis.append("")
        analysis.append("🎯 ПРИНЦИП ЧЕСТНОСТИ: Лучше знать правду о 60% честности,")
        analysis.append("   чем обманываться фиктивными 94% успеха!")
        
        return "\n".join(analysis)

async def main():
    """Главная функция честного comprehensive тестирования"""
    print("🛡️ ЧЕСТНОЕ COMPREHENSIVE ТЕСТИРОВАНИЕ KITTYCORE 3.0")
    print("=" * 60)
    print("🚀 Революция: Автоматическое обнаружение подделок в реальном времени!")
    print()
    
    # Создаём честный тестер
    tester = RealHonestToolsTester(honesty_threshold=0.7)
    
    # Запускаем комплексное тестирование
    start_time = time.time()
    results = await tester.run_honest_comprehensive_test()
    total_time = time.time() - start_time
    
    # Генерируем отчёты
    print("\n" + "="*60)
    print(tester.generate_honesty_summary())
    
    print("\n" + "="*60)
    print(tester.generate_detailed_analysis())
    
    # Сохраняем результаты
    timestamp = int(time.time())
    results_file = f"honest_comprehensive_results_{timestamp}.json"
    tester.save_honesty_results(results_file)
    
    print(f"\n💾 Все результаты сохранены в {results_file}")
    print(f"⏱️ Общее время тестирования: {total_time:.1f}с")
    
    # Итоговая статистика
    honest_count = len(tester.honest_tools)
    total_count = len(set(r['tool_name'] for r in tester.test_results))
    print(f"🎯 ИТОГ: {honest_count}/{total_count} инструментов прошли проверку честности!")

if __name__ == "__main__":
    asyncio.run(main()) 