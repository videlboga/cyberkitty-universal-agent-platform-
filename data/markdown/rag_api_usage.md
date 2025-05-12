# Примеры HTTP-запросов к RAG API

## 1. Прямой доступ к локальному API

```bash
curl -X POST http://localhost:7860/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "data": ["Что такое векторная база данных?", 5],
    "fn_index": 0,
    "session_hash": "abc123"
  }'
```

## 2. Доступ через домен (после настройки DNS)

```bash
curl -X POST http://rag.cyberkitty.tech/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "data": ["Что такое векторная база данных?", 5],
    "fn_index": 0,
    "session_hash": "abc123"
  }'
```

## 3. Пример на Python с использованием локального API

```python
import requests
import json

def search_rag(query="Что такое векторная база данных?", top_k=5):
    url = "http://localhost:7860/api/predict"
    
    # Данные для запроса
    payload = {
        "data": [query, top_k],
        "fn_index": 0,
        "session_hash": "abc123"  # Может быть любой строкой
    }
    
    # Заголовки запроса
    headers = {
        "Content-Type": "application/json",
    }
    
    # Отправка запроса
    response = requests.post(url, json=payload, headers=headers)
    
    # Проверка ответа
    if response.status_code == 200:
        result = response.json()
        return result["data"][0]  # Возвращаем форматированные результаты поиска
    else:
        return f"Ошибка запроса: {response.status_code}"

# Пример использования
results = search_rag("Что такое векторная база данных?", 3)
print(results)
```

## 4. Пример на Python с использованием доменного имени

```python
import requests
import json

def search_rag(query="Что такое векторная база данных?", top_k=5):
    url = "http://rag.cyberkitty.tech/api/predict"
    
    # Данные для запроса
    payload = {
        "data": [query, top_k],
        "fn_index": 0,
        "session_hash": "abc123"  # Может быть любой строкой
    }
    
    # Заголовки запроса
    headers = {
        "Content-Type": "application/json",
    }
    
    # Отправка запроса
    response = requests.post(url, json=payload, headers=headers)
    
    # Проверка ответа
    if response.status_code == 200:
        result = response.json()
        return result["data"][0]  # Возвращаем форматированные результаты поиска
    else:
        return f"Ошибка запроса: {response.status_code}"

# Пример использования
results = search_rag("Что такое векторная база данных?", 3)
print(results)
```

## Примечания

1. Перед использованием API через домен необходимо настроить DNS запись для поддомена `rag.cyberkitty.tech`.
2. Параметр `fn_index` должен быть равен 0, что соответствует первой функции в интерфейсе Gradio.
3. Параметр `session_hash` может быть любой уникальной строкой.
4. Результаты возвращаются в поле `data[0]` ответа JSON. 