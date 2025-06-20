#!/usr/bin/env python3
"""🏠 ПРОСТОЙ ТЕСТ ЛОКАЛЬНОЙ МОДЕЛИ - DialoGPT-medium"""

import time
import torch

print("🏠 ТЕСТ ЛОКАЛЬНОЙ МОДЕЛИ")
print("="*40)

def test_dialogpt():
    """🤖 Тест DialoGPT"""
    try:
        from transformers import AutoTokenizer, AutoModelForCausalLM
        
        model_name = "microsoft/DialoGPT-medium"
        print(f"📦 Загрузка {model_name}...")
        
        start_time = time.time()
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
            
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
        )
        
        device = "cuda" if torch.cuda.is_available() else "cpu"
        model = model.to(device)
        init_time = time.time() - start_time
        
        print(f"✅ Загружено за {init_time:.1f}с на {device}")
        
        if device == "cuda":
            allocated = torch.cuda.memory_allocated() / 1024**3
            print(f"💾 VRAM: {allocated:.1f}GB")
        
        # Тест валидации
        questions = ["Задача выполнена?", "Результат корректный?"]
        
        for q in questions:
            print(f"\n🧪 Тест: '{q}'")
            
            inputs = tokenizer.encode(q + tokenizer.eos_token, return_tensors='pt').to(device)
            
            start_time = time.time()
            with torch.no_grad():
                outputs = model.generate(
                    inputs,
                    max_length=inputs.shape[1] + 8,
                    temperature=0.1,
                    do_sample=True,
                    pad_token_id=tokenizer.eos_token_id
                )
            
            response = tokenizer.decode(outputs[0], skip_special_tokens=True)
            response = response[len(q):].strip()
            gen_time = time.time() - start_time
            
            print(f"⚡ {gen_time:.2f}с: '{response}'")
        
        print(f"\n✅ МОДЕЛЬ РАБОТАЕТ!")
        return True
        
    except Exception as e:
        print(f"❌ ОШИБКА: {e}")
        return False

if __name__ == "__main__":
    success = test_dialogpt()
    if success:
        print("\n🎯 ГОТОВ К ИНТЕГРАЦИИ!")
    else:
        print("\n⚠️ Попробуем другие варианты") 