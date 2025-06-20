#!/usr/bin/env python3
import os

def check_api_keys():
    """Проверка всех API ключей KittyCore 3.0"""
    
    keys_status = {
        "OPENROUTER_API_KEY": {
            "value": os.getenv('OPENROUTER_API_KEY'),
            "required": True,
            "description": "Основной LLM провайдер"
        },
        "REPLICATE_API_TOKEN": {
            "value": os.getenv('REPLICATE_API_TOKEN'), 
            "required": False,
            "description": "Генерация изображений AI"
        },
        "TELEGRAM_BOT_TOKEN": {
            "value": os.getenv('TELEGRAM_BOT_TOKEN'),
            "required": False, 
            "description": "Telegram боты и интеграции"
        },
        "ANTHROPIC_API_KEY": {
            "value": os.getenv('ANTHROPIC_API_KEY'),
            "required": False,
            "description": "Claude модели (опционально)"
        }
    }
    
    print("🔑 ПРОВЕРКА API КЛЮЧЕЙ KITTYCORE 3.0")
    print("=" * 50)
    
    all_required_ok = True
    
    for key_name, info in keys_status.items():
        has_key = bool(info["value"])
        is_required = info["required"]
        
        if has_key:
            masked_value = info["value"][:8] + "..." if len(info["value"]) > 8 else "***"
            status = f"✅ {masked_value}"
        elif is_required:
            status = "❌ НЕ НАЙДЕН (ОБЯЗАТЕЛЬНО!)"
            all_required_ok = False
        else:
            status = "⚠️ НЕ НАЙДЕН (опционально)"
        
        print(f"{key_name:20} {status:25} {info['description']}")
    
    print("\n" + "=" * 50)
    
    if all_required_ok:
        print("🚀 ВСЕ ОБЯЗАТЕЛЬНЫЕ КЛЮЧИ НАСТРОЕНЫ!")
        print("   KittyCore 3.0 готов к работе!")
    else:
        print("⚠️ НАСТРОЙТЕ ОБЯЗАТЕЛЬНЫЕ КЛЮЧИ!")
        print("   Минимум нужен OPENROUTER_API_KEY")
    
    print(f"\n📊 СТАТУС: {len([k for k in keys_status.values() if k['value']])}/{len(keys_status)} ключей настроено")

if __name__ == "__main__":
    check_api_keys()
