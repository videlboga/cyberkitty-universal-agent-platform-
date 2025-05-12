# Формат сценария Universal Agent Platform

Сценарий — это JSON/YAML-объект с полями:
- `name`: название сценария
- `steps`: список шагов (массив объектов)

## Пример структуры шага
```json
{
  "type": "input",           // тип шага (input, message, branch и др.)
  "text": "Введите число",    // текст для пользователя
  "next_step": 1               // явный переход к следующему шагу (по индексу)
}
```

## Ветвления и условия
- Для ветвления используйте поля `condition` (выражение на Python) и `branches` (словарь переходов):
```json
{
  "type": "branch",
  "condition": "context['x'] > 0",
  "branches": {"if": 2, "else": 3},
  "text": "Проверка x"
}
```
- Если условие истинно — переход к шагу с индексом `branches.if`, иначе — к `branches.else`.

## Переменные и context
- В каждом шаге доступен объект `context` (словарь), который накапливает все пользовательские данные.
- Передавайте значения через input_data в next_step, чтобы сохранить их в context.
- В шагах можно использовать переменные из context, например:
```json
{
  "type": "message",
  "text": "Привет, {name}!"
}
```

## Пример сценария с ветвлением
См. [docs/examples/branching_scenario.json](branching_scenario.json)

## Поддерживаемые поля шага
- `type`: тип шага (input, message, branch, ...)
- `text`: текст для пользователя
- `condition`: выражение для ветвления (Python, только context)
- `branches`: словарь переходов {"if": step_index, "else": step_index}
- `next_step`: явный переход к шагу
- любые дополнительные поля (extra = "allow")

## Пример минимального сценария
```json
{
  "name": "Минимальный сценарий",
  "steps": [
    {"type": "message", "text": "Привет!"},
    {"type": "message", "text": "Пока!"}
  ]
}
``` 