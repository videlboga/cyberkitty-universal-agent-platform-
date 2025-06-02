#!/usr/bin/env python3
"""
Удобная команда для валидации всех сценариев в проекте
"""

import os
import glob
from scenario_validator import ScenarioValidator

def main():
    print("🔍 Поиск всех YAML файлов сценариев...")
    
    # Ищем все YAML файлы
    yaml_files = []
    patterns = ["*.yaml", "*.yml", "scenarios/*.yaml", "scenarios/*.yml"]
    
    for pattern in patterns:
        yaml_files.extend(glob.glob(pattern))
    
    # Фильтруем только файлы сценариев (содержащие scenario_id)
    scenario_files = []
    for file_path in yaml_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'scenario_id:' in content or 'scenario_id ' in content:
                    scenario_files.append(file_path)
        except:
            continue
    
    if not scenario_files:
        print("❌ Не найдено файлов сценариев")
        return
    
    print(f"📝 Найдено файлов сценариев: {len(scenario_files)}")
    for f in scenario_files:
        print(f"  • {f}")
    print()
    
    # Валидируем
    validator = ScenarioValidator()
    
    all_valid = True
    total_fixes = 0
    
    for file_path in scenario_files:
        print(f"📄 Проверка: {file_path}")
        
        is_valid, fixes = validator.validate_file(file_path)
        
        if fixes:
            for fix in fixes:
                print(f"  {fix}")
                if fix.startswith("🔧"):
                    total_fixes += 1
        else:
            print("  ✅ Файл корректен")
        
        if not is_valid:
            all_valid = False
            
        print()
    
    # Итоговая сводка
    if validator.fixes_applied:
        print("📊 Сводка автоисправлений:")
        for fix in validator.fixes_applied:
            print(f"  • {fix['step_id']}: {fix['old_type']} → {fix['new_type']} ({fix['confidence']:.2f})")
        print()
    
    print(f"📈 Статистика:")
    print(f"  • Проверено файлов: {len(scenario_files)}")
    print(f"  • Применено исправлений: {total_fixes}")
    print(f"  • Поддерживаемых типов шагов: {len(validator.supported_handlers)}")
    
    if all_valid:
        print("\n🎉 Все сценарии прошли валидацию!")
        if total_fixes > 0:
            print("✨ Файлы автоматически исправлены и готовы к использованию!")
    else:
        print("\n❌ Найдены критические ошибки в некоторых сценариях")

if __name__ == "__main__":
    main() 