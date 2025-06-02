# Python_FROM_VERSION=3.11-slim
FROM python:3.11-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    # Базовые зависимости
    gcc \
    libffi-dev \
    libssl-dev \
    libpq-dev \
    curl \
    wget \
    # Зависимости для PDF генерации
    wkhtmltopdf \
    xvfb \
    # Зависимости для работы с изображениями
    libjpeg-dev \
    libpng-dev \
    # Зависимости для работы с офисными документами
    libreoffice \
    # Зависимости для работы с аудио/видео
    ffmpeg \
    # Зависимости для работы с zip/архивами
    unzip \
    zip \
    # Зависимости для работы с XML/HTML
    libxml2-dev \
    libxslt1-dev \
    # Очистка кеша
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Копирование файла зависимостей и установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN echo "Force rebuild layer 2 with all dependencies on $(date)" > /force_rebuild_2.txt

# Копирование всего остального кода приложения
COPY . .

# Указываем команду для запуска приложения (по умолчанию, может быть переопределена)
CMD ["python", "app/simple_main.py"] 