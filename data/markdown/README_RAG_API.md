# API для работы с RAG-системой по курсам

## Обзор

API для RAG-системы позволяет выполнять семантический поиск по базе знаний курсов с помощью как прямого доступа к API, так и через клиентские библиотеки.

## Доступ к системе

Система доступна через:

1. **Веб-интерфейс**: http://rag.cyberkitty.tech/ или локально по адресу http://127.0.0.1:7860

2. **API**: http://rag.cyberkitty.tech/api/predict или локально http://127.0.0.1:7860/api/predict

## API Запросы

### Формат запроса к API:

```json
{
  "data": ["Ваш запрос", 5],
  "fn_index": 0,
  "session_hash": "abc123"
}
```

Где:
- `data` - массив с двумя элементами:
  - Первый элемент - строка запроса
  - Второй элемент - количество результатов (от 1 до 10)
- `fn_index` - индекс функции (всегда 0)
- `session_hash` - случайная строка для идентификации сессии

### Формат ответа:

```json
{
  "data": [
    "### Найдено 5 результатов:\n\n#### Результат #1 (релевантность: 0.5766)\n**Курс:** Название курса\n\n**Источник:** путь/к/файлу.md\n\nТекст результата...\n\n---\n\n#### Результат #2 ...",
    null
  ],
  "duration": 0.5371389389038086,
  "is_generating": false
}
```

## Использование клиентов

В репозитории представлены два клиента для работы с API:

### 1. RAG API Client (`rag_api_client.py`)

Клиент для прямого взаимодействия с API:

```bash
python rag_api_client.py "Ваш запрос" --top-k 5 --url http://127.0.0.1:7860
```

### 2. RAG Web Client (`rag_web_client.py`)

Клиент с поддержкой различных форматов API, который пытается автоматически определить правильный формат:

```bash
python rag_web_client.py "Ваш запрос" --top-k 5 --url http://127.0.0.1:7861
```

## Настройка сервера

### Запуск сервера

Для запуска сервера используйте скрипт `start_rag_server.sh`:

```bash
sudo ./start_rag_server.sh
```

Для настройки автозапуска добавьте его в crontab:

```bash
sudo crontab -e
```

И добавьте строку:

```
@reboot /var/www/rag_system/start_rag_server.sh
```

### Настройка Nginx

Для настройки проксирования через Nginx, используйте конфигурацию `nginx_rag_config.conf`:

```bash
sudo cp nginx_rag_config.conf /etc/nginx/sites-available/rag_system.conf
sudo ln -s /etc/nginx/sites-available/rag_system.conf /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Устранение неполадок

### Проверка работы сервера

```bash
ps aux | grep rag_interface
```

### Проверка портов

```bash
netstat -tulpn | grep -E '7860|7861'
```

### Просмотр логов

```bash
tail -f /var/www/rag_system/logs/rag_server.log
``` 