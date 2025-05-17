#!/bin/bash

echo "Запускаем контейнер..."
docker-compose up -d app

echo "Ждем 2 секунды для запуска контейнера..."
sleep 2

# Создаем временный файл
echo "Создаем временную директорию и файл..."
mkdir -p tmp
cat > tmp/llm_plugin.py << 'EOF'
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
from typing import Dict, Any, List, Optional, Union
import logging

from app.core.plugin_base import PluginBase

logger = logging.getLogger(__name__)

class LLMPlugin(PluginBase):
    """LLM (Language Model) Plugin для взаимодействия с различными LLM через API"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Инициализация плагина
        
        Args:
            config: Конфигурация плагина, может содержать api_key
        """
        super().__init__(name="llm")
        
        # Получаем API ключ из конфигурации или из переменной окружения
        self.api_key = (config.get('api_key') if config else None) or os.getenv("OPENROUTER_API_KEY", "")
        
        if not self.api_key:
            logger.warning("API ключ не указан для LLMPlugin, функциональность будет ограничена")

        # Дефолтный провайдер - OpenRouter
        self.provider = "openrouter"
        self.base_url = "https://openrouter.ai/api/v1"
        
        # Модель по умолчанию
        self.default_model = "anthropic/claude-3-opus:beta"
        
        # Настройки запроса по умолчанию
        self.default_params = {
            "temperature": 0.7,
            "max_tokens": 1000
        }
    
    async def generate_text(self, 
                     prompt: str, 
                     system_prompt: Optional[str] = None,
                     model: Optional[str] = None,
                     max_tokens: Optional[int] = None,
                     temperature: Optional[float] = None) -> Optional[str]:
        """
        Генерация текста с помощью LLM
        
        Args:
            prompt: Основной запрос
            system_prompt: Системный промпт (инструкция для LLM)
            model: Название модели (по умолчанию используется self.default_model)
            max_tokens: Максимальное количество токенов для генерации
            temperature: Температура (разнообразие) генерации
            
        Returns:
            Сгенерированный текст или None в случае ошибки
        """
        try:
            import httpx
            
            # Проверяем наличие API ключа
            if not self.api_key:
                logger.error("API ключ не указан, невозможно выполнить запрос к LLM")
                return None
            
            # Используем указанную модель или модель по умолчанию
            model_name = model or self.default_model
            
            # Формируем URL запроса
            url = f"{self.base_url}/chat/completions"
            
            # Формируем параметры запроса
            messages = []
            
            # Добавляем системный промпт, если указан
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            # Добавляем основной запрос
            messages.append({"role": "user", "content": prompt})
            
            # Формируем параметры
            params = {
                "model": model_name,
                "messages": messages,
                "temperature": temperature or self.default_params["temperature"],
                "max_tokens": max_tokens or self.default_params["max_tokens"]
            }
            
            # Отправляем запрос
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": "http://localhost:8000"  # Для OpenRouter
            }
            
            logger.debug(f"Отправляем запрос к LLM: {model_name}")
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    url,
                    json=params,
                    headers=headers
                )
                
                # Проверяем успешность запроса
                if response.status_code != 200:
                    logger.error(f"Ошибка запроса к LLM: {response.status_code}, {response.text}")
                    return None
                
                # Парсим ответ
                result = response.json()
                
                # Извлекаем сгенерированный текст
                if "choices" in result and len(result["choices"]) > 0:
                    generated_text = result["choices"][0]["message"]["content"]
                    return generated_text
                else:
                    logger.error(f"Неожиданный формат ответа от LLM: {result}")
                    return None
                
        except Exception as e:
            logger.exception(f"Ошибка при генерации текста через LLM: {e}")
            return None

    async def execute_step(self, action_type: str, params: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Выполнение шага сценария
        
        Args:
            action_type: Тип действия
            params: Параметры действия
            context: Контекст выполнения
            
        Returns:
            Результат выполнения шага
        """
        logger.info(f"Выполнение шага LLM плагина: {action_type}")
        
        if action_type == "generate_text":
            prompt = params.get("prompt", "")
            
            # Обрабатываем переменные в промпте
            for key, value in context.items():
                prompt = prompt.replace(f"{{{key}}}", str(value))
            
            system_prompt = params.get("system_prompt", "")
            # Обрабатываем переменные в системном промпте
            for key, value in context.items():
                system_prompt = system_prompt.replace(f"{{{key}}}", str(value))
            
            model = params.get("model", self.default_model)
            max_tokens = params.get("max_tokens", self.default_params["max_tokens"])
            temperature = params.get("temperature", self.default_params["temperature"])
            
            result = await self.generate_text(
                prompt=prompt,
                system_prompt=system_prompt,
                model=model,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            if result:
                # Сохраняем результат в контекст, если указано имя переменной
                if "output_var" in params:
                    var_name = params["output_var"]
                    context[var_name] = result
                
                return {"success": True, "response": result}
            else:
                return {"success": False, "error": "Не удалось сгенерировать текст"}
        else:
            return {"success": False, "error": f"Неизвестный тип действия: {action_type}"}
EOF

# Останавливаем контейнер
echo "Останавливаем контейнер..."
docker-compose stop app

# Копируем файл в контейнер
echo "Копируем исправленный файл в контейнер..."
docker cp tmp/llm_plugin.py universal_agent_system_app_1:/app/app/plugins/llm_plugin.py

# Устанавливаем правильные права
echo "Устанавливаем правильные права..."
docker-compose run --rm --entrypoint "chmod 644 /app/app/plugins/llm_plugin.py" app

# Запускаем контейнер снова
echo "Запускаем контейнер снова..."
docker-compose up -d app

# Ждем 3 секунды
echo "Ждем 3 секунды..."
sleep 3

# Проверяем, запустился ли контейнер
echo "Проверяем статус контейнера..."
docker-compose ps app

# Удаляем временные файлы
echo "Удаляем временные файлы..."
rm -rf tmp

echo "Готово!" 