#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import argparse
import requests
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
import logging
import traceback
from urllib.parse import urlparse

# Настройка логирования
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename="logs/proxy_openrouter.log",
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("proxy_openrouter")

# Конфигурация OpenRouter API
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

# Настройки повторных попыток
MAX_RETRIES = 5
RETRY_DELAY = 3  # секунды

# Тестовый ответ от OpenRouter API
MOCK_RESPONSE = {
    "id": "gen-" + datetime.now().strftime("%Y%m%d%H%M%S"),
    "object": "chat.completion",
    "created": int(datetime.now().timestamp()),
    "model": "openai/gpt-3.5-turbo",
    "choices": [
        {
            "index": 0,
            "message": {
                "role": "assistant",
                "content": "Привет! Это тестовый ответ от прокси-сервера OpenRouter API. Ваш запрос был перехвачен и обработан локально."
            },
            "finish_reason": "stop"
        }
    ],
    "usage": {
        "prompt_tokens": 10,
        "completion_tokens": 25,
        "total_tokens": 35
    },
    "system_fingerprint": "fp_" + datetime.now().strftime("%Y%m%d%H%M%S"),
    "proxy_server": "openrouter_proxy_local"
}

# Режим прокси (True - использовать реальный API, False - использовать моки)
USE_REAL_API = True

# Обработчик запросов
class OpenRouterProxyHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            request_json = json.loads(post_data.decode('utf-8'))
            request_id = request_json.get("id", datetime.now().strftime("%Y%m%d%H%M%S"))
            
            logger.info(f"[{request_id}] Получен запрос: {json.dumps(request_json, ensure_ascii=False)[:200]}...")
            
            # Получаем запрос от клиента и логируем его
            prompt = "Нет промпта"
            if "messages" in request_json:
                messages = request_json["messages"]
                prompt = " | ".join([f"{m.get('role', 'user')}: {m.get('content', '')}" for m in messages])
            
            logger.info(f"[{request_id}] Запрос содержит промпт: {prompt[:200]}...")
            
            # Проверяем режим работы
            if USE_REAL_API and OPENROUTER_API_KEY:
                # Пробуем отправить запрос к реальному API с повторными попытками
                response_data = self._send_to_openrouter_with_retries(request_json, request_id)
            else:
                # Используем мок-ответ
                logger.info(f"[{request_id}] Используется мок-ответ (USE_REAL_API={USE_REAL_API}, API_KEY={'присутствует' if OPENROUTER_API_KEY else 'отсутствует'})")
                response_data = MOCK_RESPONSE.copy()
                response_data["id"] = f"gen-{request_id}"
                response_data["created"] = int(datetime.now().timestamp())
                response_data["choices"][0]["message"]["content"] = f"Ответ на ваш запрос: '{prompt[:50]}...'. Это тестовый ответ от прокси-сервера."
            
            # Отправляем ответ
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response_json = json.dumps(response_data, ensure_ascii=False)
            self.wfile.write(response_json.encode('utf-8'))
            logger.info(f"[{request_id}] Отправлен ответ: {response_json[:200]}...")
            
        except Exception as e:
            error_trace = traceback.format_exc()
            logger.error(f"Ошибка при обработке запроса: {str(e)}\n{error_trace}")
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            error_response = {
                "error": str(e),
                "error_type": type(e).__name__,
                "timestamp": datetime.now().isoformat()
            }
            self.wfile.write(json.dumps(error_response).encode('utf-8'))
    
    def _send_to_openrouter_with_retries(self, request_data, request_id):
        """
        Отправляет запрос к OpenRouter API с механизмом повторных попыток
        
        Args:
            request_data: Данные запроса
            request_id: ID запроса для логирования
            
        Returns:
            Dict: Ответ от API
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "HTTP-Referer": "https://universal-agent-system.example.com",
            "X-Title": "Universal Agent System"
        }
        
        # Копируем оригинальный запрос для пересылки на API
        api_request = request_data.copy()
        
        # Добавляем request_id, если его нет
        if "id" not in api_request:
            api_request["id"] = request_id
        
        retry_count = 0
        last_error = None
        
        while retry_count < MAX_RETRIES:
            try:
                logger.info(f"[{request_id}] Попытка {retry_count + 1}/{MAX_RETRIES} отправки запроса к OpenRouter API")
                
                # Отправляем запрос
                response = requests.post(
                    OPENROUTER_API_URL, 
                    headers=headers, 
                    json=api_request,
                    timeout=60  # Увеличенный таймаут
                )
                
                # Проверяем ответ
                if response.status_code == 200:
                    logger.info(f"[{request_id}] Получен успешный ответ от OpenRouter API (статус 200)")
                    return response.json()
                else:
                    error_message = f"API вернул статус {response.status_code}: {response.text}"
                    logger.warning(f"[{request_id}] {error_message}")
                    last_error = Exception(error_message)
                    
                    # Для определенных статусов нет смысла повторять запрос
                    if response.status_code in [400, 401, 403, 404]:
                        break
            
            except requests.RequestException as e:
                error_trace = traceback.format_exc()
                logger.warning(f"[{request_id}] Ошибка запроса к API: {str(e)}\n{error_trace}")
                last_error = e
            
            # Увеличиваем счетчик попыток
            retry_count += 1
            
            # Если есть еще попытки, ждем перед следующей
            if retry_count < MAX_RETRIES:
                time.sleep(RETRY_DELAY * retry_count)  # Экспоненциальная задержка
        
        # Если все попытки исчерпаны, возвращаем мок-ответ
        logger.error(f"[{request_id}] Все попытки отправки запроса к API исчерпаны. Последняя ошибка: {str(last_error)}")
        
        mock_response = MOCK_RESPONSE.copy()
        mock_response["id"] = f"gen-{request_id}"
        mock_response["created"] = int(datetime.now().timestamp())
        mock_response["choices"][0]["message"]["content"] = f"Не удалось получить ответ от API после {MAX_RETRIES} попыток. Ошибка: {str(last_error)}"
        mock_response["proxy_server"] = "openrouter_proxy_fallback"
        
        return mock_response

def run_server(port=8080, real_api=True, api_key=None):
    global USE_REAL_API, OPENROUTER_API_KEY
    
    # Настраиваем режим работы
    USE_REAL_API = real_api
    if api_key:
        OPENROUTER_API_KEY = api_key
    
    server_address = ('', port)
    httpd = HTTPServer(server_address, OpenRouterProxyHandler)
    
    mode = "реальным API" if USE_REAL_API and OPENROUTER_API_KEY else "мок-ответами"
    logger.info(f"Запуск прокси-сервера OpenRouter на порту {port} с {mode}")
    print(f"Прокси-сервер OpenRouter запущен на порту {port} с {mode}")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("Сервер остановлен по запросу пользователя (Ctrl+C)")
    except Exception as e:
        error_trace = traceback.format_exc()
        logger.error(f"Неожиданная ошибка сервера: {str(e)}\n{error_trace}")
    finally:
        httpd.server_close()
        logger.info("Сервер закрыт")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Прокси-сервер для OpenRouter API")
    parser.add_argument("--port", type=int, default=8080, help="Порт для запуска сервера (по умолчанию 8080)")
    parser.add_argument("--mock", action="store_true", help="Использовать мок-ответы вместо реального API")
    parser.add_argument("--api-key", type=str, help="API ключ для OpenRouter")
    args = parser.parse_args()
    
    run_server(args.port, not args.mock, args.api_key) 