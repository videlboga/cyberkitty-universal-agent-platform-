import re
import json
import os

LOG_PATH = "logs/lesson_links_extract.log"
OUT_PATH = "data/markdown/lesson_links.json"

lessons = []
current = {}

with open(LOG_PATH, encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        # Поиск заголовка урока
        m = re.match(r"^## (\d+)\. (.+)$", line)
        if m:
            if current:
                lessons.append(current)
            current = {"number": int(m.group(1)), "title": m.group(2)}
        # Поиск ссылки
        if line.startswith("Ссылка:"):
            url = line.split("Ссылка:", 1)[1].strip()
            if current is not None:
                current["url"] = url
        # Поиск ID
        if line.startswith("ID:"):
            lesson_id = line.split("ID:", 1)[1].strip()
            if current is not None:
                current["id"] = lesson_id
# Добавить последний урок
if current:
    lessons.append(current)

os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
with open(OUT_PATH, "w", encoding="utf-8") as f:
    json.dump(lessons, f, ensure_ascii=False, indent=2)

print(f"Извлечено уроков: {len(lessons)}. Сохранено в {OUT_PATH}") 