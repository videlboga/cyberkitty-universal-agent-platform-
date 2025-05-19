#!/usr/bin/env python3
import requests
import json
import sys

def create_fixed_scenario():
    # Определяем исправленный сценарий
    scenario = {
        "name": "LLM-агент базовый (исправленный)",
        "steps": [
            {
                "id": "welcome",
                "type": "telegram_message",
                "message": "👋 Привет! Я агент на основе языковой модели. Я могу помочь ответить на вопросы или сгенерировать текст на основе ваших запросов.\n\nПросто напишите свой вопрос или запрос.",
                "next_step": "wait_for_query"
            },
            {
                "id": "wait_for_query",
                "type": "input",
                "prompt": "Ваш запрос:",
                "output_var": "user_query",
                "next_step": "process_query"
            },
            {
                "id": "process_query",
                "type": "llm_query",
                "prompt": "{user_query}",
                "system_prompt": "Ты - полезный ассистент, который отвечает кратко, точно и по существу. Твои ответы всегда хорошо структурированы и содержат только проверенную информацию. Если ты не знаешь ответа, честно признай это.",
                "model": "deepseek/deepseek-chat-v3-0324:free",
                "temperature": 0.7,
                "max_tokens": 500,
                "output_var": "llm_response",
                "save_text_only": True,
                "next_step": "send_response"
            },
            {
                "id": "send_response",
                "type": "telegram_message",
                "message": "{llm_response}",
                "next_step": "ask_followup"
            },
            {
                "id": "ask_followup",
                "type": "telegram_message",
                "message": "\n\nХотите задать дополнительный вопрос?",
                "next_step": "wait_for_followup"
            },
            {
                "id": "wait_for_followup",
                "type": "input",
                "prompt": "Ваш ответ (да/нет):",
                "output_var": "user_query_followup",
                "next_step": "followup_branch"
            },
            {
                "id": "followup_branch",
                "type": "branch",
                "branches": [
                    {
                        "condition": "{user_query_followup == 'да' or user_query_followup == 'Да' or user_query_followup == 'ДА'}",
                        "next_step": "wait_for_query"
                    },
                    {
                        "condition": "default",
                        "next_step": "end_conversation"
                    }
                ]
            },
            {
                "id": "end_conversation",
                "type": "telegram_message",
                "message": "Спасибо за обращение! Если у вас возникнут другие вопросы, буду рад помочь."
            }
        ],
        "description": "Базовый сценарий для агента на основе LLM. Демонстрирует возможности работы с языковыми моделями."
    }
    
    # Создаем новый сценарий
    response = requests.post(
        "http://localhost:8000/scenarios/",
        json=scenario
    )
    
    if response.status_code != 201:
        print(f"Ошибка при создании сценария: {response.status_code}")
        return None
    
    new_scenario = response.json()
    print(f"Создан новый сценарий с ID: {new_scenario['_id']}")
    return new_scenario['_id']

if __name__ == "__main__":
    scenario_id = create_fixed_scenario()
    if scenario_id:
        print("Теперь обновите агента, чтобы использовать новый сценарий:")
        print(f"./update_agent_scenario.py <agent_id> {scenario_id}") 