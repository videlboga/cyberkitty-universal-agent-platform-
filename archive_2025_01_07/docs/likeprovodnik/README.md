# 📚 ДОКУМЕНТАЦИЯ СИСТЕМЫ ЛАЙКПРОВОДНИК

## 📋 **ОГЛАВЛЕНИЕ**

### **🎯 Основные документы:**
1. **[SYSTEM_OVERVIEW.md](SYSTEM_OVERVIEW.md)** - Общий обзор системы и архитектуры
2. **[IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md)** - План реализации и текущее состояние
3. **[USER_JOURNEYS.md](USER_JOURNEYS.md)** - Детальные пользовательские пути
4. **[TECHNICAL_SPECS.md](TECHNICAL_SPECS.md)** - Технические спецификации
5. **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** - Руководство по развертыванию

### **🔧 Технические документы:**
- **[DATABASE_SCHEMA.md](DATABASE_SCHEMA.md)** - Схемы MongoDB коллекций
- **[API_REFERENCE.md](API_REFERENCE.md)** - Справочник по API
- **[PLUGIN_INTEGRATION.md](PLUGIN_INTEGRATION.md)** - Интеграция с плагинами
- **[TESTING_GUIDE.md](TESTING_GUIDE.md)** - Руководство по тестированию

### **📊 Аналитика и мониторинг:**
- **[METRICS_DASHBOARD.md](METRICS_DASHBOARD.md)** - Метрики и дашборды
- **[PERFORMANCE_TUNING.md](PERFORMANCE_TUNING.md)** - Оптимизация производительности

---

## 🚀 **БЫСТРЫЙ СТАРТ**

### **Что такое ЛайкПроводник?**
Интеллектуальная система персонального обучения ИИ с 7 модулями:
- 🎯 **AI-Путь** - персональные планы обучения
- 🧠 **НейроЭксперт** - решение сложных задач
- 🎯 **AI-коуч** - целеполагание и рефлексия
- 💡 **Генератор лайфхаков** - практические советы
- 📚 **AI-Наставник** - структурированное обучение
- 📰 **iДайджест** - персонализированные новости
- 🛣️ **Главный роутер** - интеллектуальная маршрутизация

### **Архитектура:**
- **Движок:** SimpleScenarioEngine
- **Плагины:** Telegram, LLM, MongoDB, RAG, Scheduler
- **База данных:** MongoDB с персонализацией
- **Интерфейс:** Telegram Bot

---

## 📖 **КАК ЧИТАТЬ ДОКУМЕНТАЦИЮ**

### **Для разработчиков:**
1. Начните с [SYSTEM_OVERVIEW.md](SYSTEM_OVERVIEW.md) для понимания архитектуры
2. Изучите [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) для текущего состояния
3. Следуйте [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) для запуска

### **Для продакт-менеджеров:**
1. [SYSTEM_OVERVIEW.md](SYSTEM_OVERVIEW.md) - общее понимание системы
2. [USER_JOURNEYS.md](USER_JOURNEYS.md) - пользовательские сценарии
3. [METRICS_DASHBOARD.md](METRICS_DASHBOARD.md) - ключевые метрики

### **Для DevOps:**
1. [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - развертывание
2. [PERFORMANCE_TUNING.md](PERFORMANCE_TUNING.md) - оптимизация
3. [DATABASE_SCHEMA.md](DATABASE_SCHEMA.md) - настройка БД

---

## 🎯 **СТАТУС ДОКУМЕНТАЦИИ**

### ✅ **Готово:**
- [x] Общий обзор системы
- [x] План реализации
- [x] Архитектура данных
- [x] Команды запуска

### 🔄 **В процессе:**
- [ ] Детальные пользовательские пути
- [ ] Технические спецификации
- [ ] Руководство по развертыванию
- [ ] Схемы базы данных

### 📋 **Планируется:**
- [ ] API справочник
- [ ] Руководство по тестированию
- [ ] Метрики и дашборды
- [ ] Оптимизация производительности

---

## 🤝 **УЧАСТИЕ В РАЗРАБОТКЕ**

### **Структура сценариев:**
```
scenarios/likeprovodnik/
├── 01_main_router.json      # Главный роутер
├── 02_ai_path_onboarding.json # AI-Путь
├── 03_lifehack_generator.json # Лайфхаки
├── 04_ai_mentor.json        # Наставник
├── 05_neuroexpert.json      # НейроЭксперт
├── 06_ai_coach.json         # AI-коуч
└── 07_idigest.json          # iДайджест
```

### **Атомарные блоки:**
```
templates/atomic/
├── 01_telegram_send_message.json
├── 02_telegram_send_buttons.json
├── 03_llm_query.json
├── 04_mongo_save_data.json
├── 05_mongo_find_data.json
├── 06_rag_search.json
├── 07_conditional_branch.json
├── 08_switch_scenario.json
├── 09_scheduler_create_task.json
├── 10_log_message.json
└── 11_user_profile_load.json
```

---

## 📞 **ПОДДЕРЖКА**

### **Вопросы по документации:**
- Создайте issue в репозитории
- Укажите какой документ нуждается в уточнении
- Предложите улучшения

### **Техническая поддержка:**
- Проверьте [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) для известных проблем
- Изучите логи в папке `logs/`
- Запустите тесты: `python -m pytest tests/test_likeprovodnik/`

**ЛайкПроводник - система, которая растет вместе с документацией! 📚🚀** 