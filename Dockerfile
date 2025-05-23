# Python_FROM_VERSION=3.11-slim
FROM python:3.11-slim

WORKDIR /app

# Установка зависимостей для компиляции некоторых Python пакетов
RUN apt-get update && apt-get install -y gcc libffi-dev libssl-dev libpq-dev

# Копирование файла зависимостей и установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN echo "Force rebuild layer 1 on $(date)" > /force_rebuild_1.txt

# Копирование всего остального кода приложения
COPY . .

# Указываем команду для запуска приложения
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"] 