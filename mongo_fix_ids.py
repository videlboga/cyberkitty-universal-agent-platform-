#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mongo_fix_ids.py - Универсальный скрипт миграции для MongoDB:
- Исправляет структуру документов в коллекциях agents и scenarios,
  чтобы _id = id (строка), а не ObjectId.
- Поддерживает dry-run и логирование.

Пример использования:
  python3 mongo_fix_ids.py --uri mongodb://localhost:27017 --db agent_platform --dry-run
  python3 mongo_fix_ids.py --uri mongodb://localhost:27017 --db agent_platform
"""

import argparse
import logging
from pymongo import MongoClient
from bson import ObjectId
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

COLLECTIONS = ["agents", "scenarios"]

def fix_collection_ids(collection, dry_run=False):
    fixed = 0
    skipped = 0
    for doc in collection.find({"id": {"$exists": True}}):
        if isinstance(doc.get("_id"), ObjectId):
            new_doc = dict(doc)
            new_doc["_id"] = new_doc["id"]
            del new_doc["_id"]  # remove ObjectId
            if not dry_run:
                collection.delete_one({"_id": doc["_id"]})
                collection.insert_one(new_doc)
            fixed += 1
            logging.info(f"Перевставлен документ с id={new_doc['id']}")
        else:
            skipped += 1
    return fixed, skipped

def main():
    parser = argparse.ArgumentParser(description="Миграция MongoDB: _id = id (строка)")
    parser.add_argument("--uri", default="mongodb://localhost:27017", help="MongoDB URI")
    parser.add_argument("--db", default="agent_platform", help="Имя базы данных")
    parser.add_argument("--dry-run", action="store_true", help="Только показать, не изменять")
    args = parser.parse_args()

    client = MongoClient(args.uri)
    db = client[args.db]

    total_fixed = 0
    for coll_name in COLLECTIONS:
        collection = db[coll_name]
        fixed, skipped = fix_collection_ids(collection, dry_run=args.dry_run)
        logging.info(f"Коллекция {coll_name}: исправлено {fixed}, пропущено {skipped}")
        total_fixed += fixed

    if args.dry_run:
        logging.info("Dry-run завершён. Для применения изменений запусти без --dry-run.")
    else:
        logging.info(f"Миграция завершена. Всего исправлено: {total_fixed}")

if __name__ == "__main__":
    main() 