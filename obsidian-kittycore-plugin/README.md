# 🤖 KittyCore 3.0 - Obsidian Plugin

**Саморедуплицирующаяся агентная система прямо в Obsidian!**

## 🚀 Возможности

- 🤖 **Создание агентов** прямо в заметках Obsidian
- 📊 **Автоматическая связка** заметок через [[ссылки]]
- 🔄 **Синхронизация с KittyCore** через API
- 🎯 **Выполнение задач** с результатами в заметках
- 📈 **Граф знаний** для визуализации работы агентов

## 📥 Установка

### Автоматическая установка
1. Откройте Obsidian
2. Перейдите в Settings → Community plugins
3. Найдите "KittyCore"
4. Нажмите Install и Enable

### Ручная установка
1. Скачайте `main.js`, `manifest.json`, `styles.css`
2. Поместите их в `.obsidian/plugins/kittycore-plugin/`
3. Перезапустите Obsidian
4. Включите плагин в настройках

## ⚙️ Настройка

1. Установите API URL: `http://localhost:8000`
2. Укажите OpenRouter API ключ для LLM
3. Включите автовыполнение кода (опционально)
4. Включите синхронизацию графа

## 🎯 Быстрый старт

1. **Создать агента**: `Ctrl+P` → "Создать заметку агента"
2. **Запустить задачу**: Укажите задачу в YAML frontmatter
3. **Увидеть результат**: Агенты создадут связанные заметки

## 🔧 Команды

| Команда | Описание |
|---------|----------|
| `Создать заметку агента` | Новый агент с шаблоном |
| `Синхронизировать граф` | Обновить связи заметок |
| `Выполнить задачу` | Запуск KittyCore из заметки |

## 📊 Структура заметок

```markdown
---
type: agent
agent_name: NovaAgent
capabilities: [analysis, data]
task: "Проанализировать данные продаж"
tags: [agent, kittycore, nova]
---

# NovaAgent

## Задача
Анализ данных продаж за Q4

## Результат
[[Анализ-продаж-Q4]]

## Статистика
- Задач выполнено: 5
- Успешность: 85%
```

## 🔗 Интеграция с KittyCore

Плагин автоматически:
- Создаёт папки `Agents/`, `Tasks/`, `Results/`
- Синхронизирует статус задач
- Обновляет граф связей
- Сохраняет результаты в заметки

## 🐛 Проблемы?

- Проверьте подключение к KittyCore API
- Убедитесь что API ключ корректный
- Посмотрите логи в Developer Console (F12)

---

Made with ❤️ by **CyberKitty** for **KittyCore 3.0** 