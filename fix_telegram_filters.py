#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
fix_telegram_filters.py - Скрипт для исправления фильтров в telegram_plugin.py в зависимости от версии библиотеки

Пример использования:
  python fix_telegram_filters.py
"""

import os
import sys
import re
import importlib
import logging
from importlib.metadata import version
from pathlib import Path

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("fix_telegram_filters")

# Константы
TELEGRAM_PLUGIN_PATH = Path("app/plugins/telegram_plugin.py")
BACKUP_SUFFIX = ".bak"

def get_telegram_version():
    """Получить версию python-telegram-bot"""
    try:
        ptb_version = version("python-telegram-bot")
        logger.info(f"Обнаружена версия python-telegram-bot: {ptb_version}")
        return ptb_version
    except Exception as e:
        logger.error(f"Ошибка при получении версии python-telegram-bot: {e}")
        logger.warning("Используем версию по умолчанию: 13.0.0")
        return "13.0.0"

def create_backup(file_path):
    """Создать резервную копию файла"""
    backup_path = f"{file_path}{BACKUP_SUFFIX}"
    try:
        with open(file_path, "r", encoding="utf-8") as src:
            content = src.read()
        
        with open(backup_path, "w", encoding="utf-8") as dst:
            dst.write(content)
        
        logger.info(f"Создана резервная копия файла: {backup_path}")
        return True
    except Exception as e:
        logger.error(f"Ошибка при создании резервной копии: {e}")
        return False

def fix_filters_v13(content):
    """Исправить фильтры для версии 13.x"""
    logger.info("Применяем исправления для версии 13.x")
    
    # Регулярные выражения для замены фильтров
    replacements = [
        (r"filters\._Voice\(\)", "filters.VOICE"),
        (r"filters\._Video\(\)", "filters.VIDEO"),
        (r"filters\._Audio\(\)", "filters.AUDIO"),
        (r"filters\._Contact\(\)", "filters.CONTACT"),
        (r"filters\._Location\(\)", "filters.LOCATION"),
        (r"filters\.Document\.ALL", "filters.DOCUMENT"),
        (r"filters\.Sticker\.ALL", "filters.STICKER"),
    ]
    
    # Применяем замены
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content)
    
    return content

def fix_filters_v20(content):
    """Исправить фильтры для версии 20.x"""
    logger.info("Применяем исправления для версии 20.x")
    
    # Регулярные выражения для замены фильтров
    replacements = [
        (r"filters\.VOICE", "filters._Voice()"),
        (r"filters\.VIDEO", "filters._Video()"),
        (r"filters\.AUDIO", "filters._Audio()"),
        (r"filters\.CONTACT", "filters._Contact()"),
        (r"filters\.LOCATION", "filters._Location()"),
        (r"filters\.DOCUMENT", "filters.Document.ALL"),
        (r"filters\.STICKER", "filters.Sticker.ALL"),
    ]
    
    # Применяем замены
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content)
    
    return content

def fix_telegram_plugin():
    """Основная функция для исправления telegram_plugin.py"""
    # Проверяем существование файла
    if not os.path.exists(TELEGRAM_PLUGIN_PATH):
        logger.error(f"Файл {TELEGRAM_PLUGIN_PATH} не найден")
        return False
    
    # Получаем версию библиотеки
    ptb_version = get_telegram_version()
    major_version = int(ptb_version.split(".")[0])
    
    # Создаем резервную копию
    if not create_backup(TELEGRAM_PLUGIN_PATH):
        return False
    
    # Читаем содержимое файла
    try:
        with open(TELEGRAM_PLUGIN_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Применяем исправления в зависимости от версии
        if major_version >= 20:
            content = fix_filters_v20(content)
        else:
            content = fix_filters_v13(content)
        
        # Записываем исправленный файл
        with open(TELEGRAM_PLUGIN_PATH, "w", encoding="utf-8") as f:
            f.write(content)
        
        logger.info(f"Файл {TELEGRAM_PLUGIN_PATH} успешно исправлен для версии {ptb_version}")
        return True
    except Exception as e:
        logger.error(f"Ошибка при исправлении файла: {e}")
        return False

def main():
    """Основная функция скрипта"""
    try:
        # Проверка импорта python-telegram-bot
        try:
            import telegram
            logger.info(f"Библиотека python-telegram-bot установлена")
        except ImportError:
            logger.error("Библиотека python-telegram-bot не установлена")
            return 1
        
        # Исправляем файл
        if fix_telegram_plugin():
            logger.info("Исправления успешно применены")
            return 0
        else:
            logger.error("Не удалось применить исправления")
            return 1
    except Exception as e:
        logger.error(f"Необработанное исключение: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 