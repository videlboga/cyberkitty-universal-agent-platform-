# Python_FROM_VERSION=3.11-slim
FROM python:3.11-slim

WORKDIR /app

# Установка зависимостей для компиляции некоторых Python пакетов + curl для healthcheck
RUN apt-get update && apt-get install -y gcc libffi-dev libssl-dev libpq-dev curl

# Копирование файла зависимостей и установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN echo "Force rebuild layer 1 on $(date)" > /force_rebuild_1.txt

# Копирование всего остального кода приложения
COPY . .

# Указываем команду для запуска приложения (по умолчанию, может быть переопределена)
CMD ["python", "app/simple_main.py"] 