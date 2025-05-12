FROM python:3.11-slim
WORKDIR /app
# Установка системных библиотек для python-telegram-bot и ML
RUN apt-get update && apt-get install -y gcc libffi-dev libssl-dev libjpeg-dev zlib1g-dev && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"] 