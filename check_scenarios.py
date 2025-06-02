#!/usr/bin/env python3
import requests
import json

# Получаем все сценарии
url = "http://localhost:8085/api/v1/simple/mongo/find"
payload = {"collection": "scenarios"}
response = requests.post(url, json=payload)
data = response.json()

print(f"Найдено сценариев: {len(data['data'])}")
print("\n=== ПРОВЕРКА НА ПРОБЛЕМЫ С callback_query_data ===")

problems_found = []

for scenario in data['data']:
    scenario_id = scenario['scenario_id']
    steps = scenario.get('steps', [])
    
    for step in steps:
        if step.get('type') == 'branch':
            # Проверяем формат с conditions
            conditions = step.get('params', {}).get('conditions', [])
            for condition in conditions:
                cond_text = condition.get('condition', '')
                if 'callback_query_data' in cond_text:
                    problem = {
                        'scenario_id': scenario_id,
                        'step_id': step.get('id'),
                        'condition': cond_text,
                        'type': 'conditions'
                    }
                    problems_found.append(problem)
                    print(f"❌ ПРОБЛЕМА в {scenario_id}, шаг {step.get('id')}: {cond_text}")

if not problems_found:
    print("✅ Все сценарии используют правильный формат!")
else:
    print(f"\n📊 Найдено проблем: {len(problems_found)}")
    for problem in problems_found:
        print(f"- {problem['scenario_id']}.{problem['step_id']}") 