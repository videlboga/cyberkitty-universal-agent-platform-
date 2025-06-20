#!/usr/bin/env python3
"""
📥 ПРЯМАЯ ЗАГРУЗКА EMBEDDING МОДЕЛИ
"""

import time
from huggingface_hub import hf_hub_download
import os

def download_model():
    """Загружаем модель напрямую"""
    print("🚀 ЗАГРУЖАЕМ МОДЕЛЬ НАПРЯМУЮ...")
    
    model_name = "sentence-transformers/paraphrase-MiniLM-L3-v2"
    
    # Основные файлы модели
    files_to_download = [
        "config.json",
        "pytorch_model.bin",
        "tokenizer.json", 
        "tokenizer_config.json",
        "vocab.txt",
        "modules.json",
        "sentence_bert_config.json"
    ]
    
    start_time = time.time()
    
    for filename in files_to_download:
        try:
            print(f"📦 Загружаем {filename}...")
            
            file_path = hf_hub_download(
                repo_id=model_name,
                filename=filename,
                cache_dir="./hf_cache"
            )
            
            file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
            print(f"✅ {filename} загружен ({file_size:.1f} MB)")
            
        except Exception as e:
            print(f"⚠️ Не удалось загрузить {filename}: {e}")
    
    total_time = time.time() - start_time
    print(f"\n⏱️ Загрузка завершена за {total_time:.2f}с")
    
    # Теперь тестируем модель
    test_model()

def test_model():
    """Тестируем загруженную модель"""
    print("\n🧪 ТЕСТИРУЕМ ЗАГРУЖЕННУЮ МОДЕЛЬ...")
    
    try:
        # Указываем путь к кешу
        os.environ['HF_HOME'] = './hf_cache'
        
        from sentence_transformers import SentenceTransformer
        
        start = time.time()
        model = SentenceTransformer('sentence-transformers/paraphrase-MiniLM-L3-v2')
        end = time.time()
        
        print(f"✅ Модель загружена за {end-start:.2f}с")
        print(f"📊 Размерность: {model.get_sentence_embedding_dimension()}")
        
        # Тестируем эмбеддинги
        texts = ["программирование", "веб разработка", "базы данных"]
        embeddings = model.encode(texts)
        
        print(f"🧠 Эмбеддинги созданы: {embeddings.shape}")
        
        # Тестируем семантическую близость
        from sentence_transformers.util import cos_sim
        
        similarity = cos_sim(embeddings[0], embeddings[1])
        print(f"🔗 Сходство 'программирование' vs 'веб разработка': {similarity.item():.3f}")
        
        print("🎉 МОДЕЛЬ РАБОТАЕТ ИДЕАЛЬНО!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")
        return False

if __name__ == "__main__":
    download_model() 