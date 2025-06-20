#!/usr/bin/env python3
"""
📦 ТЕСТ ЗАГРУЗКИ EMBEDDING МОДЕЛИ
"""
import os
import time

# Настраиваем окружение
os.environ['TRANSFORMERS_OFFLINE'] = '0'
os.environ['HF_DATASETS_OFFLINE'] = '0'

print('🚀 ЗАГРУЖАЕМ EMBEDDING МОДЕЛЬ...')

try:
    from sentence_transformers import SentenceTransformer
    
    start = time.time()
    print('📦 Загружаем paraphrase-MiniLM-L3-v2...')
    
    model = SentenceTransformer('paraphrase-MiniLM-L3-v2')
    
    end = time.time()
    
    print(f'✅ Модель загружена за {end-start:.2f}с')
    print(f'📊 Размерность: {model.get_sentence_embedding_dimension()}')
    
    # Тест эмбеддинга
    print('🧠 Тестируем создание эмбеддингов...')
    embeddings = model.encode(['тест', 'программирование'])
    print(f'✅ Эмбеддинги созданы: {embeddings.shape}')
    
    print('🎉 МОДЕЛЬ РАБОТАЕТ!')
    
except Exception as e:
    print(f'❌ Ошибка: {e}')
    print('💡 Попробуем другую модель...')
    
    try:
        # Пробуем ещё более лёгкую модель
        model = SentenceTransformer('all-MiniLM-L6-v2') 
        print('✅ Загрузилась all-MiniLM-L6-v2')
    except Exception as e2:
        print(f'❌ Ошибка 2: {e2}') 