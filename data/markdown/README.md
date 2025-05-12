# RAG система для markdown документов

Система Retrieval-Augmented Generation (RAG) для поиска информации по markdown документам. Система индексирует markdown файлы, создает векторные эмбеддинги и предоставляет API для семантического поиска по содержимому.

## Функциональность

- Обработка и индексация markdown документов
- Разбиение документов на семантические чанки
- Создание векторных эмбеддингов для чанков с использованием sentence-transformers
- Индексирование с использованием FAISS для быстрого поиска
- REST API для доступа к системе

## Установка

### Требования

- Python 3.8+
- Все зависимости указаны в файле `requirements.txt`

### Установка зависимостей

```bash
pip install -r requirements.txt
```

### Настройка переменных окружения

Скопируйте пример файла `.env.example` в `.env` и отредактируйте по необходимости:

```bash
cp .env.example .env
```

## Использование

### 1. Индексация документов

Для создания индекса из markdown документов выполните:

```bash
python rag_processor.py
```

По умолчанию система ищет markdown файлы в текущей директории. Вы можете указать другую директорию, изменив параметр `data_dir` в коде.

### 2. Запуск API сервера

Для запуска API сервера выполните:

```bash
python server.py
```

Параметры запуска:
- `--host` - Хост (по умолчанию 0.0.0.0)
- `--port` - Порт (по умолчанию 8000)
- `--index-path` - Путь к индексу (по умолчанию ./index)
- `--reload` - Включить автоматическую перезагрузку при изменении файлов

Например:
```bash
python server.py --port 9000 --index-path ./my_index
```

### 3. Использование API

После запуска сервера API будет доступен по адресу `http://localhost:8000`.

#### Доступные эндпоинты:

- `GET /` - Проверка работоспособности API
- `GET /search?query=<запрос>&top_k=<число>` - Поиск по запросу методом GET
- `POST /search` - Поиск по запросу методом POST с JSON-телом

Пример запроса с использованием curl:

```bash
curl -X POST "http://localhost:8000/search" \
     -H "Content-Type: application/json" \
     -d '{"query": "Как использовать ChatGPT", "top_k": 5}'
```

Пример запроса с использованием Python:

```python
import requests

response = requests.post(
    "http://localhost:8000/search",
    json={"query": "Как использовать ChatGPT", "top_k": 5}
)

if response.status_code == 200:
    results = response.json()["results"]
    for result in results:
        print(f"Score: {result['score']}")
        print(f"Content: {result['content'][:200]}...")
        print("-" * 50)
```

## Развертывание с использованием Docker

### Сборка образа Docker

```bash
docker build -t rag-system .
```

### Запуск контейнера

```bash
docker run -p 8000:8000 -v $(pwd)/index:/app/index rag-system
```

Если вы хотите, чтобы система сначала проиндексировала документы, вы можете заменить команду запуска:

```bash
docker run -p 8000:8000 -v $(pwd):/app/data -v $(pwd)/index:/app/index \
  rag-system sh -c "python rag_processor.py && python server.py"
```

## Интеграция с LLM моделями

Данная система RAG может быть легко интегрирована с LLM моделями. Вот пример использования с OpenAI:

```python
import openai
import requests

def get_rag_response(query, api_url="http://localhost:8000/search"):
    # Получаем контекст из нашей RAG системы
    response = requests.post(
        api_url,
        json={"query": query, "top_k": 3}
    )
    
    if response.status_code != 200:
        raise Exception(f"Ошибка при запросе к RAG API: {response.text}")
    
    # Формируем контекст из результатов
    context = []
    for result in response.json()["results"]:
        context.append(result["content"])
    
    context_text = "\n\n".join(context)
    
    # Формируем промпт для модели
    prompt = f"""
    Используй следующий контекст для ответа на вопрос. 
    Если ты не можешь ответить на основе контекста, скажи, что у тебя недостаточно информации.
    
    Контекст:
    {context_text}
    
    Вопрос: {query}
    """
    
    # Запрос к OpenAI API
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Ты ассистент, отвечающий на вопросы на основе предоставленной информации."},
            {"role": "user", "content": prompt}
        ]
    )
    
    return response.choices[0].message.content

# Пример использования
answer = get_rag_response("Как использовать ChatGPT для написания текстов?")
print(answer)
```

## Лицензия

MIT 