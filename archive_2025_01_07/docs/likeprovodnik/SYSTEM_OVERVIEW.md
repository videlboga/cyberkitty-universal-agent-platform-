# 🎓 СИСТЕМА ЛАЙКПРОВОДНИК - ОБЗОР

## 🎯 **ЦЕЛЬ СИСТЕМЫ**

**ЛайкПроводник** - это интеллектуальная система персонального обучения и развития в области ИИ, построенная на базе `SimpleScenarioEngine`. Система предоставляет 7 специализированных модулей для комплексного сопровождения пользователя на пути изучения искусственного интеллекта.

---

## 🏗️ **АРХИТЕКТУРНЫЕ ПРИНЦИПЫ**

### **Основа: SimpleScenarioEngine**
- ✅ Один движок для всех модулей
- ✅ Композиция из атомарных сценариев
- ✅ Простая система плагинов
- ✅ Явная передача контекста между модулями

### **Модульность**
- 🧩 Каждый модуль - отдельный сценарий
- 🔄 Переключение между модулями через `switch_scenario`
- 📊 Общий контекст пользователя
- 🎯 Персонализация на основе профиля

### **Персонализация**
- 👤 Единый профиль пользователя в MongoDB
- 🧠 Адаптация контента под уровень знаний
- 📈 Обучение на основе истории взаимодействий
- 🎨 Персональные рекомендации через RAG

---

## 🎭 **7 МОДУЛЕЙ СИСТЕМЫ**

### **1. 🛣️ Главный роутер** (`01_main_router.json`)
**Назначение:** Интеллектуальная маршрутизация пользователей по модулям

**Логика работы:**
1. Загружает профиль пользователя
2. Проверяет, нужен ли онбординг
3. Анализирует намерения пользователя по ключевым словам
4. Направляет в соответствующий модуль

**Ключевые слова для маршрутизации:**
- `лайфхак`, `совет` → Генератор лайфхаков
- `наставник`, `урок`, `материал` → AI-Наставник  
- `задача`, `решение`, `эксперт` → НейроЭксперт
- `цель`, `коуч`, `рефлексия` → AI-коуч
- `новости`, `дайджест`, `аи` → iДайджест

### **2. 🎯 AI-Путь** (`02_ai_path_onboarding.json`)
**Назначение:** Персональный план обучения для новых пользователей

**Процесс онбординга:**
1. **Опрос (5 вопросов):**
   - Опыт в ИИ (новичок → эксперт)
   - Цели обучения (карьера, проект, развитие)
   - Доступное время (1-2 часа → 10+ часов в неделю)
   - Интересы (NLP, CV, анализ данных)
   - Предпочтения (видео, текст, практика)

2. **Анализ и генерация:**
   - RAG поиск релевантных материалов
   - LLM генерация персонального плана на 4 недели
   - Сохранение в MongoDB

3. **Результат:**
   - Структурированный план обучения в HTML
   - Конкретные шаги и ресурсы
   - Временные рамки

### **3. 💡 Генератор лайфхаков** (`03_lifehack_generator.json`)
**Назначение:** Быстрые практические советы по ИИ

**Возможности:**
- Лайфхаки по категориям (инструменты, обучение, карьера)
- Персонализация под уровень пользователя
- Сохранение понравившихся советов
- Ежедневные рекомендации

### **4. 📚 AI-Наставник** (`04_ai_mentor.json`)
**Назначение:** Структурированное обучение с материалами

**Функции:**
- Подбор обучающих материалов
- Пошаговые уроки
- Проверка понимания
- Адаптация сложности

### **5. 🧠 НейроЭксперт** (`05_neuroexpert.json`)
**Назначение:** Решение сложных задач с экспертным анализом

**Процесс решения:**
1. **Анализ задачи:**
   - Определение типа и сложности
   - Поиск похожих решений в базе
   - Оценка необходимых знаний

2. **Генерация решения:**
   - Персонализация под уровень пользователя
   - Пошаговое объяснение
   - Альтернативные подходы
   - Практические рекомендации

3. **Интерактивность:**
   - Возможность уточнений
   - Дополнительные объяснения
   - Практические примеры

### **6. 🎯 AI-коуч** (`06_ai_coach.json`)
**Назначение:** Целеполагание и рефлексия в обучении

**Коучинговый процесс:**
- Постановка SMART целей
- Планирование шагов
- Регулярная рефлексия
- Корректировка планов
- Мотивационная поддержка

### **7. 📰 iДайджест** (`07_idigest.json`)
**Назначение:** Персонализированные новости и тренды ИИ

**Контент:**
- Актуальные новости ИИ
- Анализ трендов
- Персонализация под интересы
- Еженедельные дайджесты

---

## 🔧 **ТЕХНИЧЕСКИЙ СТЕК**

### **Основные компоненты:**
- **Движок:** `SimpleScenarioEngine`
- **База данных:** MongoDB (профили, планы, решения)
- **Поиск:** RAG с векторными эмбеддингами
- **ИИ:** LLM API (Meta Llama, OpenAI)
- **Интерфейс:** Telegram Bot
- **Планировщик:** Отложенные задачи

### **Плагины:**
- `SimpleTelegramPlugin` - взаимодействие с пользователем
- `SimpleLLMPlugin` - генерация контента
- `MongoPlugin` - работа с данными
- `SimpleRAGPlugin` - семантический поиск
- `SimpleSchedulerPlugin` - планирование задач

---

## 📊 **СТРУКТУРА ДАННЫХ**

### **Основные коллекции MongoDB:**

#### **users** - Профили пользователей
```json
{
  "telegram_id": 123456789,
  "experience_level": "beginner|learning|working|expert",
  "learning_goals": ["career", "project", "development"],
  "interests": ["nlp", "cv", "data", "all"],
  "time_commitment": "low|medium|high|intensive",
  "preferred_format": "video|text|practice|mixed",
  "onboarding_completed": true,
  "created_at": "2024-12-01T10:00:00Z"
}
```

#### **learning_plans** - Персональные планы
```json
{
  "user_id": "user_123",
  "plan_html": "<h2>План обучения...</h2>",
  "modules": ["basics", "nlp", "practice"],
  "duration_weeks": 4,
  "status": "active|completed|paused"
}
```

#### **expert_solutions** - Решения НейроЭксперта
```json
{
  "user_id": "user_123",
  "task": "Как создать чат-бота?",
  "solution": "<h3>Пошаговое решение...</h3>",
  "complexity": 3,
  "personalized": true
}
```

### **RAG коллекции:**

#### **learning_materials** - Обучающие материалы
```json
{
  "title": "Основы машинного обучения",
  "content": "Машинное обучение - это...",
  "type": "article|video|course",
  "difficulty": "beginner|intermediate|advanced",
  "topics": ["ml", "basics"],
  "embedding": [0.1, 0.2, ...]
}
```

---

## 🚀 **ПОЛЬЗОВАТЕЛЬСКИЕ ПУТИ**

### **Новый пользователь:**
1. Запуск → Главный роутер
2. Определение как новый → AI-Путь онбординг
3. Прохождение опроса (5 вопросов)
4. Получение персонального плана
5. Переход к изучению материалов

### **Опытный пользователь:**
1. Запрос → Главный роутер
2. Анализ намерений по ключевым словам
3. Направление в соответствующий модуль
4. Персонализированный ответ
5. Возможность перехода в другие модули

### **Решение задачи:**
1. Вопрос → НейроЭксперт
2. Анализ сложности задачи
3. Поиск похожих решений
4. Генерация персонализированного решения
5. Интерактивные уточнения

---

## 📈 **ПРЕИМУЩЕСТВА АРХИТЕКТУРЫ**

### **Простота:**
- Один движок для всех модулей
- Понятная структура сценариев
- Легкая отладка и тестирование

### **Масштабируемость:**
- Легко добавлять новые модули
- Переиспользование атомарных блоков
- Независимость модулей друг от друга

### **Персонализация:**
- Единый профиль пользователя
- Адаптация под уровень знаний
- Обучение на истории взаимодействий

### **Гибкость:**
- Легкая настройка логики через JSON
- Возможность A/B тестирования
- Быстрое внесение изменений

---

## 🎯 **КЛЮЧЕВЫЕ МЕТРИКИ**

### **Пользовательский опыт:**
- Время до получения первого полезного ответа
- Процент завершения онбординга
- Частота возвращения пользователей
- Удовлетворенность ответами

### **Эффективность обучения:**
- Прогресс по персональным планам
- Количество решенных задач
- Достижение поставленных целей
- Применение полученных знаний

### **Техническая производительность:**
- Время ответа системы
- Успешность выполнения сценариев
- Доступность сервисов
- Качество персонализации

**ЛайкПроводник - это комплексная система для изучения ИИ, которая адаптируется под каждого пользователя и растет вместе с ним! 🚀** 