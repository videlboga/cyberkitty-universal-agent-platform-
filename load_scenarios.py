#!/usr/bin/env python3
"""
📚 ЗАГРУЗКА СЦЕНАРИЕВ ONTOBOT В БАЗУ ДАННЫХ
Скрипт для загрузки обновленных сценариев с реальными ID сообщений
"""

import os
import yaml
import json
import requests
from pathlib import Path
from loguru import logger

# Настройка логирования
logger.add("logs/scenario_loader.log", 
          format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | LOADER | {message}",
          level="INFO", rotation="10 MB", compression="zip")

class ScenarioLoader:
    """Загружает сценарии в базу данных через KittyCore API."""
    
    def __init__(self, api_base_url: str = "http://localhost:8085"):
        self.api_base_url = api_base_url
        self.scenarios_dir = Path("scenarios")
        
        logger.info("📚 Scenario Loader инициализирован")
        
    def load_yaml_scenario(self, file_path: Path) -> dict:
        """Загружает сценарий из YAML файла."""
        
        logger.info(f"📄 Загрузка сценария из {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                scenario = yaml.safe_load(f)
                
            logger.info(f"✅ Сценарий загружен: {scenario.get('scenario_id', 'unknown')}")
            return scenario
            
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки {file_path}: {str(e)}")
            return None
    
    def save_scenario_to_db(self, scenario: dict) -> bool:
        """Сохраняет сценарий в базу данных через API."""
        
        scenario_id = scenario.get('scenario_id', 'unknown')
        logger.info(f"💾 Сохранение сценария {scenario_id} в БД")
        
        try:
            url = f"{self.api_base_url}/api/v1/simple/mongo/save-scenario"
            
            payload = {
                "collection": "scenarios",
                "scenario_id": scenario_id,
                "document": scenario
            }
            
            response = requests.post(url, json=payload, timeout=30)
            result = response.json()
            
            if result.get('success'):
                logger.info(f"✅ Сценарий {scenario_id} сохранен в БД")
                return True
            else:
                logger.error(f"❌ Ошибка сохранения {scenario_id}: {result.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Ошибка запроса для {scenario_id}: {str(e)}")
            return False
    
    def load_all_scenarios(self) -> dict:
        """Загружает все сценарии из папки scenarios."""
        
        logger.info("🔄 Загрузка всех сценариев")
        
        if not self.scenarios_dir.exists():
            logger.error(f"❌ Папка {self.scenarios_dir} не найдена")
            return {"success": False, "error": "Scenarios directory not found"}
        
        results = {
            "loaded": [],
            "failed": [],
            "total": 0
        }
        
        # Ищем все YAML файлы
        yaml_files = list(self.scenarios_dir.glob("*.yaml")) + list(self.scenarios_dir.glob("*.yml"))
        
        logger.info(f"📁 Найдено YAML файлов: {len(yaml_files)}")
        
        for yaml_file in yaml_files:
            results["total"] += 1
            
            # Загружаем сценарий
            scenario = self.load_yaml_scenario(yaml_file)
            
            if scenario:
                # Сохраняем в БД
                if self.save_scenario_to_db(scenario):
                    results["loaded"].append({
                        "file": str(yaml_file),
                        "scenario_id": scenario.get('scenario_id', 'unknown')
                    })
                else:
                    results["failed"].append({
                        "file": str(yaml_file),
                        "scenario_id": scenario.get('scenario_id', 'unknown'),
                        "error": "Database save failed"
                    })
            else:
                results["failed"].append({
                    "file": str(yaml_file),
                    "scenario_id": "unknown",
                    "error": "YAML load failed"
                })
        
        logger.info(f"📊 Результаты загрузки:")
        logger.info(f"   Всего файлов: {results['total']}")
        logger.info(f"   Успешно загружено: {len(results['loaded'])}")
        logger.info(f"   Ошибок: {len(results['failed'])}")
        
        return results
    
    def check_api_connection(self) -> bool:
        """Проверяет подключение к KittyCore API."""
        
        logger.info("🔗 Проверка подключения к KittyCore API")
        
        try:
            url = f"{self.api_base_url}/health"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                logger.info("✅ KittyCore API доступен")
                return True
            else:
                logger.error(f"❌ KittyCore API недоступен: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Ошибка подключения к API: {str(e)}")
            return False

def main():
    """Главная функция для загрузки сценариев."""
    
    print("📚 ЗАГРУЗКА СЦЕНАРИЕВ ONTOBOT В БАЗУ ДАННЫХ")
    print("="*50)
    
    loader = ScenarioLoader()
    
    # Проверяем подключение к API
    print("🔗 Проверка подключения к KittyCore...")
    if not loader.check_api_connection():
        print("❌ KittyCore API недоступен. Убедитесь, что сервер запущен на порту 8085.")
        return
    
    print("✅ KittyCore API доступен")
    
    # Загружаем все сценарии
    print("\n📚 Загрузка сценариев...")
    results = loader.load_all_scenarios()
    
    # Выводим результаты
    print(f"\n📊 РЕЗУЛЬТАТЫ ЗАГРУЗКИ:")
    print("-" * 30)
    print(f"📁 Всего файлов: {results['total']}")
    print(f"✅ Успешно загружено: {len(results['loaded'])}")
    print(f"❌ Ошибок: {len(results['failed'])}")
    
    if results['loaded']:
        print(f"\n✅ УСПЕШНО ЗАГРУЖЕНЫ:")
        for item in results['loaded']:
            print(f"   📄 {item['scenario_id']} ({item['file']})")
    
    if results['failed']:
        print(f"\n❌ ОШИБКИ ЗАГРУЗКИ:")
        for item in results['failed']:
            print(f"   📄 {item['scenario_id']} ({item['file']}) - {item['error']}")
    
    # Сохраняем результаты
    with open("logs/scenario_load_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 Подробные результаты сохранены в logs/scenario_load_results.json")
    print("\n✅ Загрузка завершена!")

if __name__ == "__main__":
    main() 