#!/usr/bin/env python3
"""
🔍 АНАЛИЗ ВОЗМОЖНОСТЕЙ ЛОКАЛЬНЫХ МОДЕЛЕЙ

Проверяем что можно запустить на RTX 3070 Ti (8GB VRAM)
"""

import subprocess
import importlib
import sys

print("🔍 АНАЛИЗ СИСТЕМЫ ДЛЯ ЛОКАЛЬНЫХ LLM")
print("="*60)

# Проверяем доступные библиотеки
libraries_to_check = [
    "transformers",
    "torch", 
    "accelerate",
    "bitsandbytes",
    "sentencepiece",
    "protobuf",
    "numpy",
    "huggingface_hub"
]

print("\n📦 ПРОВЕРКА БИБЛИОТЕК:")
available_libs = {}
for lib in libraries_to_check:
    try:
        module = importlib.import_module(lib)
        version = getattr(module, '__version__', 'unknown')
        available_libs[lib] = version
        print(f"   ✅ {lib}: {version}")
    except ImportError:
        available_libs[lib] = None
        print(f"   ❌ {lib}: НЕ УСТАНОВЛЕН")

# Проверяем GPU
print(f"\n🖥️ ИНФОРМАЦИЯ О СИСТЕМЕ:")
try:
    import torch
    print(f"   🔥 CUDA: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"   🎮 GPU: {torch.cuda.get_device_name(0)}")
        print(f"   💾 VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
        print(f"   ⚡ CUDA версия: {torch.version.cuda}")
except:
    print("   ❌ PyTorch не доступен")

# Рекомендуемые модели для RTX 3070 Ti (8GB)
print(f"\n🤖 РЕКОМЕНДУЕМЫЕ ЛОКАЛЬНЫЕ МОДЕЛИ (8GB VRAM):")

models_8gb = [
    {
        "name": "microsoft/DialoGPT-medium",
        "size": "1.4GB",
        "speed": "Очень быстрая",
        "quality": "Хорошая для диалогов",
        "setup": "pip install transformers torch",
        "good_for": "Быстрые тесты, валидация"
    },
    {
        "name": "microsoft/DialoGPT-large", 
        "size": "3.0GB",
        "speed": "Быстрая",
        "quality": "Отличная для диалогов",
        "setup": "pip install transformers torch",
        "good_for": "Качественная валидация"
    },
    {
        "name": "google/flan-t5-large",
        "size": "3.0GB", 
        "speed": "Быстрая",
        "quality": "Отличная для задач",
        "setup": "pip install transformers torch",
        "good_for": "Instruction following, задачи"
    },
    {
        "name": "microsoft/CodeT5-large",
        "size": "3.0GB",
        "speed": "Быстрая", 
        "quality": "Отличная для кода",
        "setup": "pip install transformers torch",
        "good_for": "Код, программирование"
    },
    {
        "name": "mistralai/Mistral-7B-Instruct-v0.1",
        "size": "7GB",
        "speed": "Средняя",
        "quality": "Превосходная",
        "setup": "pip install transformers torch bitsandbytes",
        "good_for": "Полноценный LLM, лучшее качество"
    }
]

for i, model in enumerate(models_8gb, 1):
    print(f"\n{i}. 🤖 {model['name']}")
    print(f"   📦 Размер: {model['size']}")
    print(f"   ⚡ Скорость: {model['speed']}")
    print(f"   🎯 Качество: {model['quality']}")
    print(f"   🔧 Установка: {model['setup']}")
    print(f"   ✨ Лучше для: {model['good_for']}")

# Ollama вариант
print(f"\n🦙 АЛЬТЕРНАТИВА - OLLAMA:")
print(f"   📥 Установка: curl -fsSL https://ollama.ai/install.sh | sh")
print(f"   🤖 Модели для 8GB:")
print(f"      • llama3.2:3b (3GB) - быстрая, современная")
print(f"      • mistral:7b (7GB) - качественная")
print(f"      • codellama:7b (7GB) - для программирования")
print(f"   ⚡ Преимущества: автоустановка, оптимизация, простота")

# Рекомендации
print(f"\n🎯 РЕКОМЕНДАЦИИ ДЛЯ KITTYCORE:")

if available_libs["transformers"] and available_libs["torch"]:
    print(f"   ✅ ГОТОВО К РАБОТЕ:")
    print(f"      1. Быстрые тесты: DialoGPT-medium (1.4GB)")
    print(f"      2. Качественная валидация: FLAN-T5-large (3GB)") 
    print(f"      3. Полный LLM: Mistral-7B (7GB)")
else:
    print(f"   ⚠️ НУЖНА УСТАНОВКА:")
    missing = [lib for lib, ver in available_libs.items() if ver is None and lib in ["transformers", "torch"]]
    print(f"      pip install {' '.join(missing)}")

print(f"\n🚀 СЛЕДУЮЩИЕ ШАГИ:")
print(f"   1. Выберите модель из списка выше")
print(f"   2. Я создам интеграцию в KittyCore")
print(f"   3. Протестируем локальную работу")
print(f"   4. Настроим fallback на локальные модели")

if __name__ == "__main__":
    print(f"\n🔍 Анализ завершён. Какую модель выберете?") 