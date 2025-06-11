# 🐱 KittyCore

**Простая платформа для создания AI агентов**

> "Агент за 5 минут, сложность - по желанию"

---

## ✨ Особенности

- **🚀 Быстрый старт**: агент за 3 строки кода
- **🔧 Модульность**: добавляйте только нужные компоненты  
- **🧠 Умная память**: краткосрочная и долгосрочная память
- **🛠️ Инструменты**: расширяемая система tools
- **📡 Стриминг**: потоковые ответы
- **🌐 Мультипровайдер**: OpenAI, Anthropic, локальные модели
- **📊 Мониторинг**: встроенная телеметрия

---

## 🚀 Быстрый старт

### 1. Установка

```bash
git clone https://github.com/your-repo/kittycore
cd kittycore
pip install -e .
```

### 2. Настройка

Создайте `.env` файл:

```bash
# Один из API ключей обязателен
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key

# Опционально
DEFAULT_MODEL=gpt-4o-mini
MAX_TOKENS=1000
TEMPERATURE=0.7
```

### 3. Первый агент

```python
from kittycore import quick_agent

# Одна строка - готовый агент!
agent = quick_agent("You are a helpful assistant")
response = agent.run("Привет!")
print(response)
```

---

## 📚 Примеры

### Простой агент

```python
from kittycore import Agent

agent = Agent("You are a helpful assistant")
response = agent.run("Объясни квантовую физику простыми словами")
```

### Агент с инструментами

```python
from kittycore import Agent
from kittycore.tools import WebSearchTool, EmailTool

agent = Agent(
    prompt="You are a research assistant",
    tools=[WebSearchTool(), EmailTool()]
)

agent.run("Найди последние новости о Python и отправь сводку на email")
```

### Агент с памятью

```python
from kittycore import Agent
from kittycore.memory import PersistentMemory

agent = Agent(
    prompt="You are a personal assistant",
    memory=PersistentMemory("my_memory.db")
)

agent.run("Меня зовут Алексей")
# ... позже ...
agent.run("Как меня зовут?")  # Помнит имя!
```

### Стриминг агент

```python
agent = Agent("You are a storyteller")

for chunk in agent.stream("Расскажи историю про кота"):
    print(chunk, end="", flush=True)
```

---

## 🔧 Архитектура

KittyCore построен по принципу "простота первым делом":

```
🐱 KittyCore
├── 🤖 Agent        # Основной класс агента
├── 🧠 Memory       # Система памяти
├── 🛠️ Tools        # Инструменты и интеграции  
├── 🌐 LLM          # Провайдеры языковых моделей
└── ⚙️ Config       # Конфигурация
```

### Основные компоненты:

- **Agent**: Центральный класс для создания агентов
- **Memory**: Простая и мощная система памяти
- **Tools**: Расширяемые инструменты (веб-поиск, email, БД)
- **LLM**: Универсальные провайдеры (OpenAI, Anthropic, локальные)
- **Config**: Простая конфигурация через переменные окружения

---

## 🛠️ Создание инструментов

```python
from kittycore.tools import Tool, ToolResult

class MyTool(Tool):
    def __init__(self):
        super().__init__("my_tool", "Описание инструмента")
    
    def execute(self, param: str) -> ToolResult:
        # Ваша логика
        return ToolResult(success=True, data=f"Результат: {param}")
    
    def get_schema(self):
        return {
            "type": "object",
            "properties": {
                "param": {"type": "string", "description": "Параметр"}
            },
            "required": ["param"]
        }

# Использование
agent = Agent("You are assistant", tools=[MyTool()])
```

---

## 🧠 Типы памяти

### SimpleMemory (по умолчанию)
```python
from kittycore.memory import SimpleMemory

memory = SimpleMemory(max_entries=100)
agent = Agent("Prompt", memory=memory)
```

### PersistentMemory (с SQLite)
```python
from kittycore.memory import PersistentMemory

memory = PersistentMemory("agent_memory.db")
agent = Agent("Prompt", memory=memory)
```

---

## 🌐 Поддерживаемые модели

### OpenAI
- `gpt-4o`
- `gpt-4o-mini` 
- `gpt-4`
- `gpt-3.5-turbo`

### Anthropic
- `claude-3-opus-20240229`
- `claude-3-sonnet-20240229` 
- `claude-3-haiku-20240307`

### Локальные (через Ollama)
- `llama3`
- `mistral`
- `codellama`

```python
# Выбор модели
agent = Agent("Prompt", model="claude-3-haiku-20240307")

# Автовыбор лучшей доступной модели
agent = Agent("Prompt", model="auto")
```

---

## 📊 Мониторинг и статистика

```python
# Статистика агента
stats = agent.export_state()
print(stats)

# Статистика памяти
memory_summary = agent.get_memory_summary()
print(memory_summary)

# Статистика LLM
llm_stats = agent.llm.get_stats()
print(llm_stats)
```

---

## ⚙️ Конфигурация

### Через переменные окружения:

```bash
# LLM настройки
OPENAI_API_KEY=your_key
ANTHROPIC_API_KEY=your_key
DEFAULT_MODEL=gpt-4o-mini
MAX_TOKENS=1000
TEMPERATURE=0.7

# База данных
DATABASE_URL=sqlite:///agents.db

# Логирование
LOG_LEVEL=INFO
LOG_FILE=agent.log

# API
API_HOST=0.0.0.0
API_PORT=8080
```

### Программно:

```python
from kittycore.config import Config

config = Config(
    openai_api_key="your_key",
    default_model="gpt-4o-mini",
    max_tokens=1000
)

agent = Agent("Prompt", config=config)
```

---

## 🔄 Миграция из старой системы

Если вы использовали старую универсальную платформу:

### Было:
```python
# Сложная настройка сценариев
scenario = {
    "scenario_id": "help_bot",
    "steps": [
        {"id": "start", "type": "start", "next_step": "ask"},
        {"id": "ask", "type": "input", "next_step": "process"},
        {"id": "process", "type": "llm_query", "next_step": "end"}
    ]
}
```

### Стало:
```python
# Простой агент
agent = Agent("You are a helpful assistant")
response = agent.run("User input")
```

---

## 🚀 Продвинутые возможности

### Кастомная конфигурация агента

```python
from kittycore import Agent, AgentConfig

config = AgentConfig(
    name="my_agent",
    model="gpt-4o",
    temperature=0.9,
    max_tokens=2000,
    timeout=60
)

agent = Agent("Prompt", config=config)
```

### Несколько агентов

```python
researcher = Agent("You are a researcher", tools=[WebSearchTool()])
writer = Agent("You are a writer")
emailer = Agent("You send emails", tools=[EmailTool()])

# Пайплайн агентов
research = researcher.run("Найди информацию о Python")
article = writer.run(f"Напиши статью на основе: {research}")
emailer.run(f"Отправь статью на email: {article}")
```

---

## 🔌 Интеграции

### Telegram бот

```python
from kittycore import Agent

agent = Agent("You are a Telegram assistant")

# В вашем Telegram боте
def handle_message(message):
    response = agent.run(message.text)
    bot.reply_to(message, response)
```

### Web API

```python
from flask import Flask, request, jsonify
from kittycore import Agent

app = Flask(__name__)
agent = Agent("You are a web assistant")

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json["message"]
    response = agent.run(user_input)
    return jsonify({"response": response})
```

---

## 🧪 Тестирование

```python
import pytest
from kittycore import Agent

def test_basic_agent():
    agent = Agent("You always say 'Hello'")
    response = agent.run("Hi")
    assert "Hello" in response

def test_agent_with_memory():
    agent = Agent("Remember user names", memory=SimpleMemory())
    
    agent.run("My name is Alice")
    response = agent.run("What's my name?")
    
    assert "Alice" in response
```

---

## 🤝 Участие в разработке

1. Fork репозитория
2. Создайте ветку: `git checkout -b feature/amazing-feature`
3. Commit изменения: `git commit -am 'Add amazing feature'`
4. Push в ветку: `git push origin feature/amazing-feature`
5. Создайте Pull Request

---

## 📄 Лицензия

MIT License - можете использовать как угодно!

---

## 🙋‍♂️ Поддержка

- 📧 Email: support@kittycore.dev
- 💬 Telegram: @kittycore_support
- 🐛 Issues: [GitHub Issues](https://github.com/your-repo/kittycore/issues)
- 📖 Docs: [kittycore.dev/docs](https://kittycore.dev/docs)

---

## 🎯 Roadmap

- [ ] Веб-интерфейс для создания агентов
- [ ] Больше встроенных инструментов
- [ ] Поддержка мультиагентных систем
- [ ] Интеграция с векторными БД
- [ ] Поддержка функций (OpenAI Functions)
- [ ] Marketplace инструментов

---

**🐱 KittyCore - где сложность становится простой!**