# Шаблон: Регистрация пользователя

Универсальный шаблон для сбора данных пользователя и сохранения в MongoDB с валидацией и настраиваемыми полями.

## 🎯 Назначение

Этот шаблон создаёт интерактивный процесс регистрации, который:
- Собирает обязательные данные (имя, email)
- Предлагает заполнить опциональные поля (телефон, возраст, город)
- Валидирует введённые данные
- Сохраняет результат в MongoDB
- Предоставляет подтверждение регистрации

## 📋 Поля данных

### Обязательные поля
- **Имя** - минимум 2 символа
- **Email** - базовая валидация на наличие @ и точки

### Опциональные поля
- **Телефон** - можно пропустить
- **Возраст** - число от 1 до 120, можно пропустить
- **Город** - текст, можно пропустить

## 🔧 Настройка

### 1. Скопируйте шаблон
```bash
cp templates/user_registration/scenario.json scenarios/my_registration.json
```

### 2. Настройте параметры
Отредактируйте `initial_context` в JSON файле:

```json
{
  "initial_context": {
    "greeting": "Ваше приветствие",
    "collection_name": "your_collection",
    "required_fields": ["name", "email", "custom_field"],
    "optional_fields": ["phone", "age", "city", "other_field"]
  }
}
```

### 3. Добавьте новые поля
Чтобы добавить новое поле:

1. **Добавьте шаг ввода:**
```json
{
  "id": "get_new_field",
  "type": "input", 
  "params": {
    "prompt": "Введите новое поле:",
    "input_type": "text",
    "output_var": "new_field"
  },
  "next_step": "save_user"
}
```

2. **Обновите шаг сохранения:**
```json
{
  "id": "save_user",
  "type": "mongo_insert_one",
  "params": {
    "document": {
      "name": "{user_name}",
      "email": "{user_email}",
      "new_field": "{new_field}",
      "created_at": "{current_timestamp}"
    }
  }
}
```

### 4. Создайте агента
```bash
curl -X POST "http://localhost:8000/api/v1/agents/" \
  -H "Content-Type: application/json" \
  -d @templates/user_registration/agent_config.json
```

## 🧪 Тестирование

### Загрузка сценария
```bash
curl -X POST "http://localhost:8000/api/v1/scenarios/" \
  -H "Content-Type: application/json" \
  -d @scenarios/my_registration.json
```

### Создание агента
```bash
curl -X POST "http://localhost:8000/api/v1/agents/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Агент регистрации",
    "scenario_id": "my_registration", 
    "plugins": ["MongoDBPlugin"],
    "initial_context": {}
  }'
```

### Запуск сценария
```bash
# Получите agent_id из предыдущего ответа
curl -X POST "http://localhost:8000/api/v1/agent-actions/{agent_id}/execute" \
  -H "Content-Type: application/json" \
  -d '{}'
```

## 📊 Структура данных в MongoDB

После регистрации в коллекции будет сохранён документ:

```json
{
  "_id": "ObjectId(...)",
  "name": "Иван Петров",
  "email": "ivan@example.com", 
  "phone": "+7900123456",
  "age": "25",
  "city": "Москва",
  "registration_date": "2024-12-01T10:30:00Z",
  "status": "active"
}
```

## 🔀 Варианты использования

### Простая регистрация (только имя и email)
Удалите шаги `get_phone`, `get_age`, `get_city` и соответствующие обработчики.

### Расширенная регистрация
Добавьте поля: профессия, интересы, аватар, социальные сети и т.д.

### Регистрация с подтверждением email
Добавьте шаги для отправки кода подтверждения и его валидации.

### Многошаговая регистрация
Разбейте на несколько экранов с промежуточным сохранением.

## ⚠️ Важные замечания

1. **Валидация данных**: Добавьте более строгую валидацию для production
2. **Безопасность**: Не храните пароли в открытом виде
3. **GDPR**: Добавьте согласие на обработку данных
4. **Дубликаты**: Проверяйте уникальность email перед сохранением

## 🔗 Связанные шаблоны

- `llm_chat` - использует данные пользователя для персонализации
- `survey` - расширенная форма с множественным выбором
- `orchestrator` - может вызывать регистрацию как под-сценарий 