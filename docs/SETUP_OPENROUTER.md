# 🚀 Настройка OpenRouter для KittyCore 3.0

## 📋 Быстрая настройка

### 1. Получить API ключ (БЕСПЛАТНО!)

1. Идем на https://openrouter.ai
2. Создаем аккаунт
3. Переходим в Keys: https://openrouter.ai/keys  
4. Создаем новый ключ (название: "KittyCore")
5. Копируем ключ (формат: `sk-or-v1-...`)

### 2. Настройка в системе

```bash
# Экспорт в текущей сессии
export OPENROUTER_API_KEY='sk-or-v1-ваш-реальный-ключ-здесь'

# Или добавить в ~/.bashrc для постоянной настройки
echo 'export OPENROUTER_API_KEY="sk-or-v1-ваш-реальный-ключ-здесь"' >> ~/.bashrc
source ~/.bashrc
```

### 3. Проверка настройки

```bash
python3 kittycore_cli_no_mocks.py
```

## 🆓 Бесплатные модели (НАВСЕГДА!)

OpenRouter предоставляет БЕСПЛАТНЫЕ модели:

### 🥇 Рекомендуемые
- **`deepseek/deepseek-chat`** - основная модель (стабильная, быстрая)
- **`deepseek/deepseek-r1`** - модель рассуждений (умная, медленная)

### 🏃 Альтернативы
- **`google/gemini-flash-1.5`** - быстрая Google модель
- **`qwen/qwen-2.5-coder-32b-instruct`** - для программирования

## 💰 Лимиты и тарифы

- **🆓 Бесплатные модели**: Без лимитов навсегда!
- **💎 Платные модели**: Claude-3.5-Sonnet, GPT-4o и другие
- **🔄 Без подписки**: Плати только за использование

## 🧪 Тестирование

### Без API ключа - честный провал:
```bash
unset OPENROUTER_API_KEY
python3 kittycore_cli_no_mocks.py
# ❌ КРИТИЧЕСКАЯ ОШИБКА: OPENROUTER_API_KEY не найден!
```

### С API ключом - реальная работа:
```bash
export OPENROUTER_API_KEY='ваш-ключ'
python3 kittycore_cli_no_mocks.py
# ✅ Система работает с настоящими LLM!
```

## 🔧 Конфигурация моделей

Система автоматически использует **`deepseek/deepseek-chat`** по умолчанию.

Для смены модели:
```python
# В коде
agent = Agent(model="deepseek/deepseek-r1")

# Через переменную среды  
export DEFAULT_MODEL="google/gemini-flash-1.5"
```

## 🚫 NO MOCKS POLICY

KittyCore 3.0 работает **ЧЕСТНО**:
- ✅ Есть API ключ → Реальные LLM запросы
- ❌ Нет API ключа → Система падает с ошибкой
- 🚫 **НИКАКИХ МОКОВ** - только правда!

## 🎯 Готовые команды

```bash
# 1. Настройка
export OPENROUTER_API_KEY='sk-or-v1-ваш-ключ'

# 2. Тест системы
python3 test_intellectual_agent.py

# 3. Интерактивный CLI
python3 kittycore_cli_no_mocks.py

# 4. Проверка моделей
python3 -c "from kittycore.llm import get_free_models; print(get_free_models())"
```

## 🆘 Решение проблем

### Ошибка 401 "No auth credentials"
- Проверить правильность API ключа
- Убедиться что ключ экспортирован: `echo $OPENROUTER_API_KEY`

### Ошибка 429 "Rate limit"
- Подождать минуту и повторить
- Использовать другую бесплатную модель

### Ошибка 400 "Bad request"  
- Проверить формат ключа (`sk-or-v1-...`)
- Создать новый ключ на сайте

---

**🎉 После настройки у вас будет полностью работающая система с реальным LLM интеллектом!** 