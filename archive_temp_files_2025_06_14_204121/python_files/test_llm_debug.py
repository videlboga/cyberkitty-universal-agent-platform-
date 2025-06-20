#!/usr/bin/env python3
"""
🔍 ДИАГНОСТИКА LLM ПРОБЛЕМ
Простой тест для выявления проблем с LLM API
"""

import sys
import json
sys.path.append('.')

from kittycore.llm import get_llm_provider

def test_simple_llm():
    """Простой тест LLM"""
    print("🔍 ДИАГНОСТИКА LLM")
    print("=" * 50)
    
    try:
        # Получаем провайдер
        llm = get_llm_provider()
        print(f"✅ LLM провайдер создан: {type(llm).__name__}")
        print(f"📝 Модель: {llm.config.model}")
        print(f"🔑 API ключ: {llm.api_key[:10]}..." if llm.api_key else "❌ Нет API ключа")
        
        # Простой запрос
        print(f"\n🧠 Тест 1: Простой запрос")
        simple_prompt = "Ответь одним словом: сколько будет 2+2?"
        
        response = llm.complete(simple_prompt)
        print(f"📤 Запрос: {simple_prompt}")
        print(f"📥 Ответ: '{response}'")
        print(f"📏 Длина ответа: {len(response)} символов")
        
        if response and len(response.strip()) > 0:
            print("✅ Простой запрос работает!")
        else:
            print("❌ Простой запрос вернул пустой ответ!")
            return False
            
        # JSON запрос
        print(f"\n🧠 Тест 2: JSON запрос")
        json_prompt = """
Верни JSON ответ в формате:
{
    "result": "success",
    "number": 42
}

Только JSON, никакого дополнительного текста!
"""
        
        response = llm.complete(json_prompt)
        print(f"📤 Запрос: JSON структура")
        print(f"📥 Ответ: '{response}'")
        
        # Пробуем парсить JSON
        try:
            # Очищаем ответ от markdown
            clean_response = response.strip()
            if "```json" in clean_response:
                start = clean_response.find("```json") + 7
                end = clean_response.find("```", start)
                clean_response = clean_response[start:end].strip()
            elif "```" in clean_response:
                start = clean_response.find("```") + 3
                end = clean_response.rfind("```")
                clean_response = clean_response[start:end].strip()
            
            # Ищем JSON в ответе
            if "{" in clean_response:
                start = clean_response.find("{")
                end = clean_response.rfind("}") + 1
                clean_response = clean_response[start:end]
            
            parsed = json.loads(clean_response)
            print(f"✅ JSON парсинг успешен: {parsed}")
            return True
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON парсинг неудачен: {e}")
            print(f"🔍 Чистый ответ: '{clean_response}'")
            return False
            
    except Exception as e:
        print(f"❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
        return False

def test_task_analysis():
    """Тест анализа задач (как в IntellectualAgent)"""
    print(f"\n🧠 Тест 3: Анализ задач")
    print("=" * 50)
    
    try:
        llm = get_llm_provider()
        
        prompt = """
Проанализируй задачу и выбери подходящие инструменты.

ЗАДАЧА: "Создать сайт с котятами"

ДОСТУПНЫЕ ИНСТРУМЕНТЫ:
{
  "file_manager": "Создание, чтение, запись файлов",
  "code_generator": "Генерация Python скриптов и HTML страниц",
  "web_search": "Поиск информации в интернете"
}

Верни JSON ответ в формате:
{
    "task_type": "creation",
    "intent": "создание сайта с котятами",
    "chosen_tools": ["code_generator", "file_manager"],
    "reasoning": "нужно создать HTML файлы"
}

ТОЛЬКО JSON, никакого дополнительного текста!
"""
        
        response = llm.complete(prompt)
        print(f"📥 Ответ LLM: '{response}'")
        
        # Парсим как в IntellectualAgent
        try:
            clean_response = response.strip()
            
            if "```json" in clean_response:
                json_start = clean_response.find("```json") + 7
                json_end = clean_response.find("```", json_start)
                json_str = clean_response[json_start:json_end].strip()
            else:
                start = clean_response.find("{")
                end = clean_response.rfind("}") + 1
                json_str = clean_response[start:end]
            
            analysis = json.loads(json_str)
            print(f"✅ Анализ задачи успешен:")
            print(f"  🎯 Тип: {analysis.get('task_type')}")
            print(f"  💡 Цель: {analysis.get('intent')}")
            print(f"  🔧 Инструменты: {analysis.get('chosen_tools')}")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка парсинга анализа: {e}")
            print(f"🔍 Чистый JSON: '{json_str if 'json_str' in locals() else 'не найден'}'")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка анализа задач: {e}")
        return False

def main():
    print("🚀 ДИАГНОСТИКА ПРОБЛЕМ LLM")
    print("Проверяем почему система не работает...")
    print("=" * 60)
    
    # Тест 1: Простой запрос
    test1_ok = test_simple_llm()
    
    # Тест 2: Анализ задач
    test2_ok = test_task_analysis()
    
    print(f"\n📊 РЕЗУЛЬТАТЫ ДИАГНОСТИКИ:")
    print(f"✅ Простой LLM: {'ОК' if test1_ok else 'ОШИБКА'}")
    print(f"✅ Анализ задач: {'ОК' if test2_ok else 'ОШИБКА'}")
    
    if test1_ok and test2_ok:
        print(f"\n🎉 LLM РАБОТАЕТ КОРРЕКТНО!")
        print(f"Проблема не в LLM, а в другом месте системы.")
    else:
        print(f"\n⚠️ НАЙДЕНЫ ПРОБЛЕМЫ С LLM!")
        print(f"Нужно исправить LLM провайдер или промпты.")

if __name__ == "__main__":
    main() 