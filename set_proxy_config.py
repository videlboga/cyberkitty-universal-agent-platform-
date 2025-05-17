#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import argparse
import docker
import logging
import tempfile
import subprocess
import time

# Настройка логирования
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename="logs/set_proxy_config.log",
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("set_proxy_config")

def update_openrouter_config(container_name, proxy_url, use_proxy=True):
    """
    Обновляет конфигурацию OpenRouter в контейнере
    
    Args:
        container_name (str): Имя контейнера Docker
        proxy_url (str): URL прокси-сервера OpenRouter
        use_proxy (bool): Использовать ли прокси (True) или оригинальный API (False)
    """
    try:
        client = docker.from_env()
        container = client.containers.get(container_name)
        
        logger.info(f"Обновление конфигурации OpenRouter в контейнере {container_name}")
        
        # Создаем новый скрипт openrouter.py с поддержкой прокси
        openrouter_py_content = '''
# -*- coding: utf-8 -*-
import os
import json
import requests
from typing import Dict, Any, List, Optional

# Конфигурация API
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_URL = os.getenv("OPENROUTER_URL", "https://openrouter.ai/api/v1/chat/completions")

# Конфигурация прокси
USE_PROXY = {use_proxy}
OPENROUTER_PROXY_URL = "{proxy_url}"

def openrouter_chat(
    prompt: str, 
    model: str = "openai/gpt-3.5-turbo", 
    max_tokens: int = 1000,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Отправляет запрос к OpenRouter API
    
    Args:
        prompt: Текст запроса
        model: Модель для использования
        max_tokens: Максимальное количество токенов в ответе
        api_key: API ключ (опционально, если не указан в переменных окружения)
    
    Returns:
        Dict содержащий ответ от API
    """
    # Используем переданный API ключ или берем из переменных окружения
    api_key = api_key or OPENROUTER_API_KEY
    
    # Формируем запрос
    headers = {{
        "Content-Type": "application/json",
        "Authorization": f"Bearer {{api_key}}",
        "HTTP-Referer": "https://universal-agent-system.example.com",
        "X-Title": "Universal Agent System"
    }}
    
    payload = {{
        "model": model,
        "messages": [{{"role": "user", "content": prompt}}],
        "max_tokens": max_tokens
    }}
    
    # Выбираем URL в зависимости от настроек прокси
    url = OPENROUTER_PROXY_URL if USE_PROXY else OPENROUTER_URL
    
    # Отправляем запрос
    response = requests.post(url, headers=headers, json=payload)
    
    # Проверяем ответ
    if response.status_code != 200:
        raise Exception(f"Ошибка API: {{response.status_code}} - {{response.text}}")
    
    return response.json()

def openrouter_models(api_key: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Получает список доступных моделей от OpenRouter API
    
    Args:
        api_key: API ключ (опционально, если не указан в переменных окружения)
    
    Returns:
        List содержащий информацию о моделях
    """
    # Используем переданный API ключ или берем из переменных окружения
    api_key = api_key or OPENROUTER_API_KEY
    
    # Формируем запрос
    headers = {{
        "Content-Type": "application/json",
        "Authorization": f"Bearer {{api_key}}",
        "HTTP-Referer": "https://universal-agent-system.example.com",
        "X-Title": "Universal Agent System"
    }}
    
    # В режиме прокси возвращаем фиктивный список моделей
    if USE_PROXY:
        return [
            {{
                "id": "openai/gpt-3.5-turbo",
                "name": "GPT-3.5 Turbo (Proxy)",
                "description": "Быстрая модель с хорошим соотношением цена/качество (прокси-версия)",
                "context_length": 16385,
                "pricing": {{"input": 0.0, "output": 0.0}}
            }},
            {{
                "id": "openai/gpt-4",
                "name": "GPT-4 (Proxy)",
                "description": "Наиболее мощная модель OpenAI (прокси-версия)",
                "context_length": 8192,
                "pricing": {{"input": 0.0, "output": 0.0}}
            }}
        ]
    
    # Отправляем запрос к API моделей
    url = "https://openrouter.ai/api/v1/models"
    response = requests.get(url, headers=headers)
    
    # Проверяем ответ
    if response.status_code != 200:
        raise Exception(f"Ошибка API: {{response.status_code}} - {{response.text}}")
    
    return response.json().get("data", [])
'''.format(use_proxy="True" if use_proxy else "False", proxy_url=proxy_url)

        # Создаем временный файл с новым содержимым
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as tmp_file:
            tmp_file.write(openrouter_py_content)
            tmp_file_path = tmp_file.name
        
        logger.info(f"Создан временный файл: {tmp_file_path}")
        
        # Копируем временный файл в контейнер с помощью docker cp
        cmd = f"docker cp {tmp_file_path} {container_name}:/app/app/integrations/openrouter.py"
        result = subprocess.run(cmd, shell=True, capture_output=True)
        
        if result.returncode != 0:
            logger.error(f"Ошибка при копировании файла: {result.stderr.decode()}")
            raise Exception(f"Ошибка docker cp: {result.stderr.decode()}")
        
        # Удаляем временный файл
        os.unlink(tmp_file_path)
        
        logger.info(f"Файл openrouter.py обновлен в контейнере {container_name}")
        
        # Перезапускаем контейнер
        container.restart()
        logger.info(f"Контейнер {container_name} перезапущен")
        
        # Даем контейнеру время на запуск
        time.sleep(5)
        
        return True
    
    except Exception as e:
        logger.error(f"Ошибка при обновлении конфигурации: {str(e)}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Настройка прокси для OpenRouter API")
    parser.add_argument("--container", type=str, default="universal_agent_system_app_1", 
                      help="Имя контейнера Docker (по умолчанию universal_agent_system_app_1)")
    parser.add_argument("--proxy-url", type=str, default="http://host.docker.internal:8080/api/v1/chat/completions", 
                      help="URL прокси-сервера OpenRouter")
    parser.add_argument("--disable-proxy", action="store_true", 
                      help="Отключить прокси и использовать реальный API")
    
    args = parser.parse_args()
    
    result = update_openrouter_config(
        container_name=args.container,
        proxy_url=args.proxy_url,
        use_proxy=not args.disable_proxy
    )
    
    if result:
        print(f"Конфигурация успешно обновлена в контейнере {args.container}")
        print(f"{'Включен режим прокси' if not args.disable_proxy else 'Используется реальный API'}")
    else:
        print("Ошибка при обновлении конфигурации. Проверьте логи.") 