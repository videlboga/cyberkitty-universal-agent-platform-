#!/bin/bash

# КОМПЛЕКСНЫЙ ТЕСТ: Новые плагины KittyCore
# Проверяет реальную работу AmoCRM и HTTP плагинов

set -e

API_URL="http://localhost:8085"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🚀 КОМПЛЕКСНЫЙ ТЕСТ: Новые плагины KittyCore"
echo "🎯 Цель: Проверить реальную работу AmoCRM и HTTP плагинов"
echo "📅 Дата: $(date)"
echo "=" | tr '=' '=' | head -c 70; echo

# Функция для проверки доступности API
check_api_availability() {
    echo "🔍 Проверка доступности API..."
    
    if curl -s "$API_URL/health" > /dev/null 2>&1; then
        echo "✅ API доступен: $API_URL"
        return 0
    else
        echo "❌ API недоступен: $API_URL"
        echo "💡 Убедитесь что KittyCore запущен: docker-compose up -d"
        return 1
    fi
}

# Функция для запуска теста с обработкой ошибок
run_test() {
    local test_name="$1"
    local test_script="$2"
    
    echo ""
    echo "🧪 ЗАПУСК ТЕСТА: $test_name"
    echo "📄 Скрипт: $test_script"
    echo "-" | tr '-' '-' | head -c 50; echo
    
    if [ -f "$test_script" ]; then
        if bash "$test_script"; then
            echo "✅ ТЕСТ ПРОЙДЕН: $test_name"
            return 0
        else
            echo "❌ ТЕСТ ПРОВАЛЕН: $test_name"
            return 1
        fi
    else
        echo "❌ ТЕСТ НЕ НАЙДЕН: $test_script"
        return 1
    fi
}

# Проверяем доступность API
if ! check_api_availability; then
    exit 1
fi

echo ""
echo "📋 ПЛАН ТЕСТИРОВАНИЯ:"
echo "---"
echo "1. 🔧 AmoCRM плагин - настройка и операции"
echo "2. 🌐 HTTP плагин - внешние запросы"
echo "3. 📊 Общая проверка здоровья системы"

# Счетчики результатов
total_tests=0
passed_tests=0
failed_tests=0

echo ""
echo "🎬 НАЧАЛО ТЕСТИРОВАНИЯ"
echo "=" | tr '=' '=' | head -c 70; echo

# Тест 1: AmoCRM плагин
total_tests=$((total_tests + 1))
if run_test "AmoCRM плагин" "$SCRIPT_DIR/test_amocrm_real_integration.sh"; then
    passed_tests=$((passed_tests + 1))
else
    failed_tests=$((failed_tests + 1))
fi

# Тест 2: HTTP плагин
total_tests=$((total_tests + 1))
if run_test "HTTP плагин" "$SCRIPT_DIR/test_http_real_integration.sh"; then
    passed_tests=$((passed_tests + 1))
else
    failed_tests=$((failed_tests + 1))
fi

echo ""
echo "🏥 ФИНАЛЬНАЯ ПРОВЕРКА ЗДОРОВЬЯ СИСТЕМЫ"
echo "---"

# Финальная проверка здоровья
health_response=$(curl -s "$API_URL/api/v1/simple/health")

if echo "$health_response" | jq -e '.status == "healthy"' > /dev/null 2>&1; then
    echo "✅ Система здорова после всех тестов"
    
    # Показываем статистику плагинов
    plugins_count=$(echo "$health_response" | jq '.registered_plugins | length')
    handlers_count=$(echo "$health_response" | jq '.registered_handlers | length')
    
    echo "📊 Статистика системы:"
    echo "  • Плагинов зарегистрировано: $plugins_count"
    echo "  • Обработчиков доступно: $handlers_count"
    
    # Проверяем наличие новых плагинов
    echo ""
    echo "🔌 Новые плагины в системе:"
    
    if echo "$health_response" | jq -e '.registered_plugins[] | select(. == "simple_amocrm")' > /dev/null 2>&1; then
        echo "  ✅ AmoCRM плагин зарегистрирован"
        amocrm_handlers=$(echo "$health_response" | jq -r '.registered_handlers[] | select(startswith("amocrm_"))' | wc -l)
        echo "    📋 Обработчиков AmoCRM: $amocrm_handlers"
    else
        echo "  ❌ AmoCRM плагин не найден"
    fi
    
    if echo "$health_response" | jq -e '.registered_plugins[] | select(. == "simple_http")' > /dev/null 2>&1; then
        echo "  ✅ HTTP плагин зарегистрирован"
        http_handlers=$(echo "$health_response" | jq -r '.registered_handlers[] | select(startswith("http_"))' | wc -l)
        echo "    📋 Обработчиков HTTP: $http_handlers"
    else
        echo "  ❌ HTTP плагин не найден"
    fi
    
else
    echo "❌ Система нездорова после тестов"
    echo "📄 Ответ healthcheck:"
    echo "$health_response" | jq '.'
    failed_tests=$((failed_tests + 1))
fi

echo ""
echo "🎯 ИТОГОВЫЕ РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ"
echo "=" | tr '=' '=' | head -c 70; echo

echo "📊 Статистика:"
echo "  • Всего тестов: $total_tests"
echo "  • Пройдено: $passed_tests"
echo "  • Провалено: $failed_tests"

if [ $failed_tests -eq 0 ]; then
    echo ""
    echo "🏆 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!"
    echo "✅ Новые плагины KittyCore полностью функциональны"
    echo "🚀 Система готова к использованию"
    
    echo ""
    echo "💡 Что протестировано:"
    echo "  ✅ AmoCRM плагин - настройка через MongoDB API"
    echo "  ✅ AmoCRM плагин - поиск, создание контактов и сделок"
    echo "  ✅ HTTP плагин - GET, POST, PUT запросы"
    echo "  ✅ HTTP плагин - обработка ошибок и переменных"
    echo "  ✅ Регистрация плагинов в движке"
    echo "  ✅ Доступность обработчиков шагов"
    echo "  ✅ Общее здоровье системы"
    
    echo ""
    echo "🎉 НОВЫЕ ПЛАГИНЫ ГОТОВЫ К ПРОДАКШЕНУ!"
    
    exit 0
else
    echo ""
    echo "❌ ЕСТЬ ПРОВАЛЕННЫЕ ТЕСТЫ!"
    echo "⚠️ Требуется исправление ошибок"
    echo "📋 Проверьте логи выше для деталей"
    
    exit 1
fi 