#!/usr/bin/env python3
"""
🚀 ПРИМЕР API ЗАПРОСА ДЛЯ АНАЛИЗА БИТРИКС24
Демонстрация как система получает запросы нативно
"""

import requests
import json
import time

# Конфигурация KittyCore API
KITTYCORE_API_URL = "http://localhost:8085"
CHANNEL_ID = "telegram_channel_1"

def send_bitrix_analysis_request():
    """Отправка запроса на анализ рынка Битрикс24"""
    
    print("🚀 ОТПРАВКА ЗАПРОСА НА АНАЛИЗ БИТРИКС24")
    print("=" * 50)
    
    # Payload для запуска сценария анализа
    payload = {
        "user_id": "user_bitrix_analyst",
        "chat_id": "chat_bitrix_project", 
        "scenario_id": "bitrix_market_analysis",
        "context": {
            "user_message": "Проанализируй рынок приложений Битрикс24 и создай прототипы с улучшенным UX",
            "project_type": "market_analysis",
            "target_platform": "bitrix24",
            "analysis_depth": "comprehensive",
            "deliverables": [
                "market_research",
                "competitor_analysis", 
                "ux_audit",
                "prototypes",
                "technical_specs"
            ]
        }
    }
    
    print(f"📤 Отправка запроса на {KITTYCORE_API_URL}")
    print(f"🎯 Сценарий: {payload['scenario_id']}")
    print(f"👤 Пользователь: {payload['user_id']}")
    print(f"💬 Запрос: {payload['context']['user_message']}")
    
    try:
        # Отправляем запрос к KittyCore API
        response = requests.post(
            f"{KITTYCORE_API_URL}/api/v1/simple/channels/{CHANNEL_ID}/execute",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"\n📥 Ответ от сервера:")
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Успех: {result.get('success', False)}")
            print(f"   🎯 Сценарий: {result.get('scenario_id', 'unknown')}")
            print(f"   💬 Сообщение: {result.get('message', 'Нет сообщения')}")
            
            if result.get('final_context'):
                context = result['final_context']
                print(f"\n📊 РЕЗУЛЬТАТ МАРШРУТИЗАЦИИ:")
                
                if 'selected_agent' in context:
                    print(f"   🤖 Выбранный агент: {context['selected_agent']}")
                    print(f"   🎯 Сценарий агента: {context.get('agent_scenario', 'не указан')}")
                    print(f"   🔧 Метод: {context.get('routing_method', 'unknown')}")
                
                if 'request_type' in context:
                    print(f"   📋 Тип запроса: {context['request_type']}")
            
            return result
        else:
            print(f"   ❌ Ошибка: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Ошибка соединения: {e}")
        return None

def monitor_scenario_execution(scenario_id: str, timeout: int = 60):
    """Мониторинг выполнения сценария"""
    
    print(f"\n🔍 МОНИТОРИНГ ВЫПОЛНЕНИЯ СЦЕНАРИЯ: {scenario_id}")
    print("-" * 50)
    
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            # Запрашиваем статус выполнения
            response = requests.get(
                f"{KITTYCORE_API_URL}/api/v1/simple/info",
                timeout=10
            )
            
            if response.status_code == 200:
                info = response.json()
                print(f"🔄 Система активна: {info.get('status', 'unknown')}")
                
                # В реальности здесь был бы специальный endpoint для статуса сценария
                # Например: /api/v1/simple/scenarios/{scenario_id}/status
                
            time.sleep(5)  # Проверяем каждые 5 секунд
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Ошибка мониторинга: {e}")
            break
    
    print(f"⏰ Мониторинг завершен (таймаут: {timeout}с)")

def demonstrate_native_requests():
    """Демонстрация нативных запросов к системе"""
    
    print("🎯 ДЕМОНСТРАЦИЯ НАТИВНОЙ РАБОТЫ С KITTYCORE")
    print("=" * 60)
    
    # 1. Отправляем запрос на анализ
    result = send_bitrix_analysis_request()
    
    if result and result.get('success'):
        scenario_id = result.get('scenario_id')
        
        print(f"\n✅ Запрос принят системой!")
        print(f"🎯 ID сценария: {scenario_id}")
        
        # 2. Мониторим выполнение
        if scenario_id:
            monitor_scenario_execution(scenario_id, timeout=30)
        
        # 3. Показываем как система обрабатывает другие типы запросов
        demonstrate_additional_requests()
    else:
        print(f"\n❌ Запрос не был принят системой")

def demonstrate_additional_requests():
    """Демонстрация дополнительных типов запросов"""
    
    print(f"\n🧪 ДОПОЛНИТЕЛЬНЫЕ ТИПЫ ЗАПРОСОВ")
    print("-" * 40)
    
    # Различные типы запросов, которые система может получать
    additional_requests = [
        {
            "name": "Быстрый анализ конкурента",
            "payload": {
                "scenario_id": "quick_competitor_analysis",
                "context": {
                    "user_message": "Найди информацию о приложении 'CRM Analytics' в Битрикс24 маркете",
                    "analysis_type": "competitor_single"
                }
            }
        },
        {
            "name": "Создание прототипа",
            "payload": {
                "scenario_id": "prototype_creation",
                "context": {
                    "user_message": "Создай wireframes для мобильного CRM приложения",
                    "design_type": "wireframes",
                    "platform": "mobile"
                }
            }
        },
        {
            "name": "Техническая спецификация",
            "payload": {
                "scenario_id": "technical_specification",
                "context": {
                    "user_message": "Напиши техническое описание API интеграции с Битрикс24",
                    "doc_type": "technical_spec",
                    "integration_target": "bitrix24_api"
                }
            }
        }
    ]
    
    for req in additional_requests:
        print(f"\n📋 {req['name']}:")
        print(f"   🎯 Сценарий: {req['payload']['scenario_id']}")
        print(f"   💬 Запрос: {req['payload']['context']['user_message']}")
        
        # В реальности здесь бы отправлялись запросы
        print(f"   📤 [Симуляция отправки запроса...]")

def show_system_architecture():
    """Показ архитектуры обработки запросов"""
    
    print(f"\n🏗️ АРХИТЕКТУРА ОБРАБОТКИ ЗАПРОСОВ")
    print("=" * 50)
    
    architecture_flow = [
        "1. 📥 Входящий запрос → API endpoint (/api/v1/simple/channels/{channel_id}/execute)",
        "2. 🧠 LLM Router Plugin → Классификация запроса (llm_classify_request)",
        "3. 🎯 Умная маршрутизация → Выбор агента (llm_route_task)", 
        "4. 🔄 Переключение сценария → Агент-специфичный сценарий",
        "5. 🤖 Выполнение агентом → Специализированная обработка",
        "6. 📊 Сбор результатов → Компиляция отчета",
        "7. 📤 Ответ пользователю → channel_action (send_message)"
    ]
    
    for step in architecture_flow:
        print(f"   {step}")
    
    print(f"\n🔧 КЛЮЧЕВЫЕ КОМПОНЕНТЫ:")
    print(f"   • SimpleScenarioEngine - основной движок выполнения")
    print(f"   • SimpleLLMRouterPlugin - плагин умной маршрутизации")
    print(f"   • Agent Scenarios - специализированные сценарии агентов")
    print(f"   • Channel Plugins - интерфейсы ввода/вывода")

if __name__ == "__main__":
    print("🚀 KITTYCORE NATIVE REQUEST DEMONSTRATION")
    print("Демонстрация нативной работы с запросами")
    print("=" * 60)
    
    # Показываем архитектуру
    show_system_architecture()
    
    # Демонстрируем работу (симуляция, так как сервер может быть не запущен)
    print(f"\n⚠️  ВНИМАНИЕ: Это демонстрация архитектуры")
    print(f"   Для реальной работы нужен запущенный KittyCore сервер на порту 8085")
    
    # demonstrate_native_requests()  # Раскомментировать при запущенном сервере 