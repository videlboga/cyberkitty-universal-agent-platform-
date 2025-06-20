#!/usr/bin/env python3
"""
🔧 ИСПРАВЛЕННАЯ ВЕРСИЯ UNIFIED_ORCHESTRATOR

ПРОБЛЕМА: Валидатор не штрафует за поддельные отчёты, давая высокие оценки
РЕШЕНИЕ: Жёсткие штрафы за подделки, критический провал при 50%+ подделок

Изменения в _validate_file_contents:
1. Приоритет проверки подделок ПЕРЕД проверкой содержимого
2. Жёсткий штраф -0.25 за каждую подделку
3. Критический провал при 50%+ подделок (-0.5 балла)
4. Подделки НЕ получают бонусы за валидное содержимое
"""

# Импортируем оригинальный модуль
import sys
import os
sys.path.append(os.path.dirname(__file__))

from unified_orchestrator import *

class FixedUnifiedOrchestrator(UnifiedOrchestrator):
    """Исправленная версия с жёсткими штрафами за подделки"""
    
    async def _validate_file_contents(self, created_files: List[str], task: str, expected_outcome: Dict) -> Dict[str, Any]:
        """
        ИСПРАВЛЕННАЯ валидация содержимого файлов - ЖЁСТКИЕ ШТРАФЫ ЗА ПОДДЕЛКИ!
        
        Проверяет что файлы содержат РЕАЛЬНЫЙ контент, а не отчёты под нужными расширениями.
        НОВИНКА: КРИТИЧЕСКИЙ ПРОВАЛ при обнаружении подделок!
        """
        score_bonus = 0.0
        details = []
        issues = []
        fake_files_count = 0
        total_files_count = 0
        
        for file_path in created_files:
            try:
                # Читаем содержимое файла
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                else:
                    issues.append(f"❌ Файл не найден: {file_path}")
                    continue
                
                total_files_count += 1
                
                # СНАЧАЛА проверяем на подделки - ЭТО ПРИОРИТЕТ!
                fake_report_check = self._detect_fake_reports(content, file_path, task)
                if fake_report_check['is_fake']:
                    fake_files_count += 1
                    issues.append(f"🚨 ПОДДЕЛКА: {file_path}: {fake_report_check['reason']}")
                    # ЖЁСТКИЙ ШТРАФ за подделку - минус от базового балла!
                    score_bonus -= 0.25  # Каждая подделка = -25% от базового балла
                    continue  # Не даём бонусы за поддельные файлы!
                
                # Только если файл НЕ подделка - проверяем содержимое
                file_ext = os.path.splitext(file_path)[1].lower()
                content_check = self._check_content_by_extension(file_path, content, file_ext, task)
                
                if content_check['is_valid']:
                    score_bonus += content_check['bonus']
                    details.append(f"✅ {file_path}: {content_check['reason']}")
                else:
                    issues.append(f"❌ {file_path}: {content_check['reason']}")
                    score_bonus -= 0.05  # Малый штраф за невалидное содержимое
                
                details.append(f"✅ {file_path}: содержимое аутентично")
                
            except Exception as e:
                issues.append(f"❌ Ошибка чтения {file_path}: {e}")
        
        # КРИТИЧЕСКАЯ ЛОГИКА: Если много подделок - результат провален!
        fake_ratio = fake_files_count / max(total_files_count, 1)
        
        if fake_ratio >= 0.5:  # 50%+ подделок = критический провал
            score_bonus = -0.5  # Огромный штраф
            issues.append(f"🚨 КРИТИЧЕСКИЙ ПРОВАЛ: {fake_files_count}/{total_files_count} файлов - подделки!")
        elif fake_ratio >= 0.3:  # 30%+ подделок = серьёзные проблемы
            score_bonus -= 0.2  # Дополнительный штраф
            issues.append(f"⚠️ СЕРЬЁЗНЫЕ ПРОБЛЕМЫ: {fake_files_count}/{total_files_count} файлов - подделки!")
        elif fake_ratio > 0:  # Любые подделки = предупреждение
            issues.append(f"⚠️ НАЙДЕНЫ ПОДДЕЛКИ: {fake_files_count}/{total_files_count} файлов")
        
        logger.info(f"📊 Валидация файлов: {total_files_count} всего, {fake_files_count} подделок ({fake_ratio*100:.1f}%), бонус: {score_bonus:.3f}")
        
        return {
            'score_bonus': score_bonus,  # Убираем ограничение max() - штрафы должны работать!
            'details': details,
            'issues': issues,
            'fake_files_count': fake_files_count,
            'total_files_count': total_files_count,
            'fake_ratio': fake_ratio
        }

def create_fixed_orchestrator(config: UnifiedConfig = None) -> FixedUnifiedOrchestrator:
    """Создание исправленного оркестратора"""
    if config is None:
        config = UnifiedConfig()
    return FixedUnifiedOrchestrator(config)

async def solve_with_fixed_orchestrator(task: str, **kwargs) -> Dict[str, Any]:
    """Решение задачи через исправленный оркестратор"""
    orchestrator = create_fixed_orchestrator()
    return await orchestrator.solve_task(task, **kwargs) 