# 🔑 ПОЛНЫЙ ГАЙД ПО API КЛЮЧАМ KITTYCORE 3.0

## 📋 **ОБЗОР НЕОБХОДИМЫХ КЛЮЧЕЙ**

KittyCore 3.0 работает **БЕЗ API ключей** (9/9 базовых инструментов), но для **расширенной функциональности** нужны:

### 🎯 **ОБЯЗАТЕЛЬНЫЙ КЛЮЧ (для LLM)**
- **`OPENROUTER_API_KEY`** - основной LLM провайдер (БЕСПЛАТНО!)

### 🚀 **РАСШИРЕННЫЕ ВОЗМОЖНОСТИ**
- **`REPLICATE_API_TOKEN`** - генерация изображений AI
- **`TELEGRAM_BOT_TOKEN`** - Telegram боты и интеграции  
- **`ANTHROPIC_API_KEY`** - Claude модели (опционально)

---

## 🆓 **1. OPENROUTER API KEY (БЕСПЛАТНО!)**

### **Зачем нужен:**
- Основной LLM провайдер для агентов
- Доступ к **БЕСПЛАТНЫМ** моделям навсегда
- Замена дорогих OpenAI/Anthropic API

### **Получение ключа:**

1. **Регистрация** (30 секунд):
   ```bash
   # Открыть в браузере
   chromium https://openrouter.ai
   ```

2. **Создание ключа**:
   - Перейти в **Keys**: https://openrouter.ai/keys
   - Нажать **"Create Key"**
   - Название: `KittyCore-3.0`
   - Скопировать ключ (формат: `sk-or-v1-...`)

3. **Настройка в системе**:
   ```bash
   # Экспорт в текущей сессии
   export OPENROUTER_API_KEY='sk-or-v1-ваш-реальный-ключ-здесь'
   
   # Постоянная настройка в ~/.bashrc
   echo 'export OPENROUTER_API_KEY="sk-or-v1-ваш-реальный-ключ-здесь"' >> ~/.bashrc
   source ~/.bashrc
   ```

### **БЕСПЛАТНЫЕ модели (НАВСЕГДА!):**
- **`deepseek/deepseek-chat`** - основная модель (стабильная, быстрая)
- **`deepseek/deepseek-r1`** - модель рассуждений (умная, медленная)
- **`google/gemini-flash-1.5`** - быстрая Google модель
- **`qwen/qwen-2.5-coder-32b-instruct`** - для программирования

### **Проверка:**
```bash
python3 -c "
import os
print('✅ OPENROUTER_API_KEY настроен!' if os.getenv('OPENROUTER_API_KEY') else '❌ OPENROUTER_API_KEY НЕ найден!')
"
```

---

## 🎨 **2. REPLICATE API TOKEN (для генерации изображений)**

### **Зачем нужен:**
- Генерация изображений через AI (FLUX, Imagen, Ideogram)
- Топовые модели 2025 года
- Без ключа работает **демо режим**

### **Получение ключа:**

1. **Регистрация**:
   ```bash
   chromium https://replicate.com
   ```

2. **Создание токена**:
   - Перейти в **Account** → **API tokens**
   - Нажать **"Create token"**
   - Название: `KittyCore-ImageGen`
   - Скопировать токен (формат: `r8_...`)

3. **Настройка**:
   ```bash
   # Экспорт в текущей сессии
   export REPLICATE_API_TOKEN='r8_ваш-реальный-токен-здесь'
   
   # Постоянная настройка
   echo 'export REPLICATE_API_TOKEN="r8_ваш-реальный-токен-здесь"' >> ~/.bashrc
   source ~/.bashrc
   ```

### **Тарифы:**
- **🆓 Бесплатный тир**: $10 кредитов при регистрации
- **💰 Стоимость**: ~$0.003-0.02 за изображение
- **🎯 Модели**: FLUX-Schnell (дешёвая), FLUX-Pro (качественная)

### **Проверка:**
```bash
python3 -c "
import os
print('✅ REPLICATE_API_TOKEN настроен!' if os.getenv('REPLICATE_API_TOKEN') else '⚠️ REPLICATE_API_TOKEN НЕ найден - демо режим')
"
```

---

## 📱 **3. TELEGRAM BOT TOKEN (для Telegram интеграций)**

### **Зачем нужен:**
- Создание Telegram ботов
- Отправка уведомлений
- Интеграция с каналами/чатами
- Без ключа **недоступно**

### **Получение токена:**

1. **Создание бота**:
   ```bash
   # Открыть Telegram и найти @BotFather
   # Или по ссылке:
   chromium https://t.me/BotFather
   ```

2. **Команды в BotFather**:
   ```
   /start
   /newbot
   Название: KittyCore Agent Bot
   Username: kittycore_agent_bot (должен быть уникальным)
   ```

3. **Копирование токена**:
   - BotFather выдаст токен (формат: `1234567890:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`)
   - **СОХРАНИТЬ ТОКЕН!**

4. **Настройка**:
   ```bash
   # Экспорт в текущей сессии
   export TELEGRAM_BOT_TOKEN='1234567890:ваш-реальный-токен-здесь'
   
   # Постоянная настройка
   echo 'export TELEGRAM_BOT_TOKEN="1234567890:ваш-реальный-токен-здесь"' >> ~/.bashrc
   source ~/.bashrc
   ```

### **Дополнительные зависимости:**
```bash
# Установка библиотек для Telegram
pip install pyrogram aiohttp aiofiles
```

### **Проверка:**
```bash
python3 -c "
import os
print('✅ TELEGRAM_BOT_TOKEN настроен!' if os.getenv('TELEGRAM_BOT_TOKEN') else '❌ TELEGRAM_BOT_TOKEN НЕ найден!')
"
```

---

## 🤖 **4. ANTHROPIC API KEY (опционально)**

### **Зачем нужен:**
- Прямой доступ к Claude моделям
- Альтернатива OpenRouter (если нужна)
- **НЕ ОБЯЗАТЕЛЬНО** - OpenRouter уже включает Claude

### **Получение ключа:**

1. **Регистрация**:
   ```bash
   chromium https://console.anthropic.com
   ```

2. **Создание ключа**:
   - **API Keys** → **Create Key**
   - Название: `KittyCore-Claude`
   - Скопировать ключ (формат: `sk-ant-...`)

3. **Настройка**:
   ```bash
   # Экспорт в текущей сессии
   export ANTHROPIC_API_KEY='sk-ant-ваш-реальный-ключ-здесь'
   
   # Постоянная настройка
   echo 'export ANTHROPIC_API_KEY="sk-ant-ваш-реальный-ключ-здесь"' >> ~/.bashrc
   source ~/.bashrc
   ```

### **Тарифы:**
- **🆓 Бесплатный тир**: $5 кредитов при регистрации
- **💰 Стоимость**: ~$0.003-0.015 за 1K токенов

---

## 📁 **5. НАСТРОЙКА ЧЕРЕЗ .ENV ФАЙЛ**

Создать файл `.env` в корне проекта:

```bash
# Создание .env файла
cat > .env << 'EOF'
# === ОСНОВНОЙ LLM ПРОВАЙДЕР ===
OPENROUTER_API_KEY=sk-or-v1-ваш-реальный-ключ-здесь

# === РАСШИРЕННЫЕ ВОЗМОЖНОСТИ ===
REPLICATE_API_TOKEN=r8_ваш-реальный-токен-здесь
TELEGRAM_BOT_TOKEN=1234567890:ваш-реальный-токен-здесь

# === ОПЦИОНАЛЬНО ===
ANTHROPIC_API_KEY=sk-ant-ваш-реальный-ключ-здесь

# === НАСТРОЙКИ LLM ===
DEFAULT_MODEL=deepseek/deepseek-chat
MAX_TOKENS=1000
TEMPERATURE=0.7

# === НАСТРОЙКИ API ===
API_HOST=0.0.0.0
API_PORT=8080
LOG_LEVEL=INFO
EOF
```

---

## 🧪 **6. ПРОВЕРКА ВСЕХ КЛЮЧЕЙ**

Создать скрипт проверки:

```bash
cat > check_api_keys.py << 'EOF'
#!/usr/bin/env python3
import os

def check_api_keys():
    """Проверка всех API ключей KittyCore 3.0"""
    
    keys_status = {
        "OPENROUTER_API_KEY": {
            "value": os.getenv('OPENROUTER_API_KEY'),
            "required": True,
            "description": "Основной LLM провайдер"
        },
        "REPLICATE_API_TOKEN": {
            "value": os.getenv('REPLICATE_API_TOKEN'), 
            "required": False,
            "description": "Генерация изображений AI"
        },
        "TELEGRAM_BOT_TOKEN": {
            "value": os.getenv('TELEGRAM_BOT_TOKEN'),
            "required": False, 
            "description": "Telegram боты и интеграции"
        },
        "ANTHROPIC_API_KEY": {
            "value": os.getenv('ANTHROPIC_API_KEY'),
            "required": False,
            "description": "Claude модели (опционально)"
        }
    }
    
    print("🔑 ПРОВЕРКА API КЛЮЧЕЙ KITTYCORE 3.0")
    print("=" * 50)
    
    all_required_ok = True
    
    for key_name, info in keys_status.items():
        has_key = bool(info["value"])
        is_required = info["required"]
        
        if has_key:
            masked_value = info["value"][:8] + "..." if len(info["value"]) > 8 else "***"
            status = f"✅ {masked_value}"
        elif is_required:
            status = "❌ НЕ НАЙДЕН (ОБЯЗАТЕЛЬНО!)"
            all_required_ok = False
        else:
            status = "⚠️ НЕ НАЙДЕН (опционально)"
        
        print(f"{key_name:20} {status:25} {info['description']}")
    
    print("\n" + "=" * 50)
    
    if all_required_ok:
        print("🚀 ВСЕ ОБЯЗАТЕЛЬНЫЕ КЛЮЧИ НАСТРОЕНЫ!")
        print("   KittyCore 3.0 готов к работе!")
    else:
        print("⚠️ НАСТРОЙТЕ ОБЯЗАТЕЛЬНЫЕ КЛЮЧИ!")
        print("   Минимум нужен OPENROUTER_API_KEY")
    
    print(f"\n📊 СТАТУС: {len([k for k in keys_status.values() if k['value']])}/{len(keys_status)} ключей настроено")

if __name__ == "__main__":
    check_api_keys()
EOF

# Запуск проверки
python3 check_api_keys.py
```

---

## 🚀 **7. БЫСТРЫЙ СТАРТ (МИНИМУМ)**

Для **быстрого старта** нужен только **OPENROUTER_API_KEY**:

```bash
# 1. Получить БЕСПЛАТНЫЙ ключ OpenRouter (30 секунд)
chromium https://openrouter.ai/keys

# 2. Настроить ключ
export OPENROUTER_API_KEY='sk-or-v1-ваш-ключ'

# 3. Проверить работу
python3 check_api_keys.py

# 4. Запустить KittyCore
python3 kittycore_cli.py
```

---

## 💰 **8. СТОИМОСТЬ И ЛИМИТЫ**

### **БЕСПЛАТНЫЕ ВОЗМОЖНОСТИ:**
- **OpenRouter**: Бесплатные модели навсегда
- **Replicate**: $10 кредитов при регистрации  
- **Telegram**: Полностью бесплатно
- **Anthropic**: $5 кредитов при регистрации

### **ПРИМЕРНАЯ СТОИМОСТЬ:**
```
📝 Текстовые задачи:    $0.001-0.01 за задачу
🎨 Генерация изображений: $0.003-0.02 за изображение  
📱 Telegram сообщения:   $0 (бесплатно)
🤖 Claude запросы:       $0.003-0.015 за 1K токенов
```

### **РЕКОМЕНДАЦИИ:**
1. **Начать с OpenRouter** (бесплатные модели)
2. **Добавить Replicate** при необходимости изображений
3. **Telegram** - по потребности в ботах
4. **Anthropic** - только если нужен прямой доступ к Claude

---

## ✅ **ИТОГОВЫЙ ЧЕКЛИСТ**

- [ ] **OPENROUTER_API_KEY** настроен (ОБЯЗАТЕЛЬНО)
- [ ] **REPLICATE_API_TOKEN** настроен (для изображений) 
- [ ] **TELEGRAM_BOT_TOKEN** настроен (для ботов)
- [ ] **ANTHROPIC_API_KEY** настроен (опционально)
- [ ] **.env файл** создан с ключами
- [ ] **check_api_keys.py** показывает ✅
- [ ] **KittyCore 3.0** запускается без ошибок

**🎉 ПОЗДРАВЛЯЕМ! KittyCore 3.0 готов к полноценной работе!**

---

## 🆘 **ПОМОЩЬ И ПОДДЕРЖКА**

### **Проблемы с ключами:**
- Проверить формат ключей (правильные префиксы)
- Убедиться в отсутствии лишних пробелов
- Перезапустить терминал после настройки

### **Ошибки API:**
- Проверить лимиты и баланс аккаунтов
- Попробовать другие модели (если превышены лимиты)
- Использовать fallback на бесплатные модели

### **Telegram проблемы:**
- Установить зависимости: `pip install pyrogram aiohttp aiofiles`
- Проверить правильность токена бота
- Убедиться что бот активен

**КittyCore 3.0 - самая мощная саморедуплицирующаяся агентная система! 🐱🚀** 