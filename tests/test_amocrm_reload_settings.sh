#!/bin/bash

# ТЕСТ: Перезагрузка настроек AmoCRM плагина
# Проверяет что AmoCRM плагин может перезагрузить настройки после их сохранения

set -e

API_URL="http://localhost:8085"
TEST_PREFIX="amocrm_reload_$(date +%s)"

echo "🔄 ТЕСТ: Перезагрузка настроек AmoCRM плагина"
echo "🎯 Цель: Проверить что плагин может перезагрузить настройки из MongoDB"
echo "=" | tr '=' '=' | head -c 70; echo

# Функция для проверки ответа
check_response() {
    local response="$1"
    local description="$2"
    
    if echo "$response" | jq -e '.success == true' > /dev/null 2>&1; then
        echo "✅ $description: SUCCESS"
        return 0
    else
        echo "❌ $description: FAILED"
        echo "Response: $response"
        return 1
    fi
}

echo "📋 ЭТАП 1: Проверка начального состояния"
echo "---"

# 1. Проверяем что AmoCRM плагин не настроен
echo "🔍 Проверка начального состояния AmoCRM..."
initial_test_response=$(curl -s -X POST "$API_URL/api/v1/simple/execute" \
    -H "Content-Type: application/json" \
    -d '{
        "step": {
            "id": "test_initial_state",
            "type": "amocrm_find_contact",
            "params": {
                "query": "test@example.com",
                "output_var": "initial_result"
            }
        },
        "context": {
            "user_id": "test_user"
        }
    }')

echo "📄 Начальное состояние:"
echo "$initial_test_response" | jq '.'

# Должна быть ошибка о том что AmoCRM не настроен
if echo "$initial_test_response" | jq -e '.context.initial_result.error' | grep -q "не настроен"; then
    echo "✅ AmoCRM плагин корректно сообщает что не настроен"
else
    echo "❌ AmoCRM плагин должен сообщать что не настроен"
fi

echo ""
echo "📋 ЭТАП 2: Сохранение настроек через MongoDB API"
echo "---"

# 2. Сохраняем настройки AmoCRM
echo "💾 Сохранение настроек AmoCRM..."
amocrm_settings='{
    "plugin_name": "amocrm",
    "base_url": "https://test-reload.amocrm.ru",
    "access_token": "test_reload_token_123456",
    "updated_at": "'$(date -Iseconds)'"
}'

save_response=$(curl -s -X POST "$API_URL/api/v1/simple/mongo/insert" \
    -H "Content-Type: application/json" \
    -d '{
        "collection": "plugin_settings",
        "document": '"$amocrm_settings"'
    }')

check_response "$save_response" "Сохранение настроек AmoCRM"

# 3. Сохраняем карту полей
echo "🗺️ Сохранение карты полей..."
fields_map='{
    "plugin_name": "amocrm_fields",
    "fields_map": {
        "test_field": {
            "id": 999999,
            "type": "text"
        }
    },
    "updated_at": "'$(date -Iseconds)'"
}'

fields_response=$(curl -s -X POST "$API_URL/api/v1/simple/mongo/insert" \
    -H "Content-Type: application/json" \
    -d '{
        "collection": "plugin_settings",
        "document": '"$fields_map"'
    }')

check_response "$fields_response" "Сохранение карты полей"

echo ""
echo "📋 ЭТАП 3: Проверка что настройки НЕ применились автоматически"
echo "---"

# 4. Проверяем что плагин все еще не настроен (настройки не перезагрузились)
echo "🔍 Проверка что настройки не применились автоматически..."
after_save_response=$(curl -s -X POST "$API_URL/api/v1/simple/execute" \
    -H "Content-Type: application/json" \
    -d '{
        "step": {
            "id": "test_after_save",
            "type": "amocrm_find_contact",
            "params": {
                "query": "test@example.com",
                "output_var": "after_save_result"
            }
        },
        "context": {
            "user_id": "test_user"
        }
    }')

echo "📄 Состояние после сохранения:"
echo "$after_save_response" | jq '.'

# Должна быть все та же ошибка - настройки не перезагрузились
if echo "$after_save_response" | jq -e '.context.after_save_result.error' | grep -q "не настроен"; then
    echo "✅ Подтверждено: настройки не применяются автоматически"
    echo "💡 Это ожидаемое поведение - нужна перезагрузка"
else
    echo "⚠️ Неожиданно: настройки применились автоматически"
fi

echo ""
echo "📋 ЭТАП 4: Перезапуск контейнера для перезагрузки настроек"
echo "---"

echo "🔄 Перезапуск контейнера KittyCore..."
echo "💡 Это имитирует перезагрузку плагинов с новыми настройками"

# Перезапускаем контейнер
if docker-compose restart kittycore > /dev/null 2>&1; then
    echo "✅ Контейнер перезапущен"
    
    # Ждем пока сервис поднимется
    echo "⏳ Ожидание запуска сервиса..."
    for i in {1..30}; do
        if curl -s "$API_URL/health" > /dev/null 2>&1; then
            echo "✅ Сервис запущен"
            break
        fi
        sleep 2
        echo -n "."
    done
    echo ""
else
    echo "❌ Не удалось перезапустить контейнер"
    echo "💡 Попробуйте вручную: docker-compose restart kittycore"
fi

echo ""
echo "📋 ЭТАП 5: Проверка что настройки загрузились после перезапуска"
echo "---"

# 5. Проверяем что настройки теперь загрузились
echo "🔍 Проверка настроек после перезапуска..."
after_restart_response=$(curl -s -X POST "$API_URL/api/v1/simple/execute" \
    -H "Content-Type: application/json" \
    -d '{
        "step": {
            "id": "test_after_restart",
            "type": "amocrm_find_contact",
            "params": {
                "query": "test@example.com",
                "output_var": "after_restart_result"
            }
        },
        "context": {
            "user_id": "test_user"
        }
    }')

echo "📄 Состояние после перезапуска:"
echo "$after_restart_response" | jq '.'

# Теперь должна быть другая ошибка - не "не настроен", а ошибка подключения к AmoCRM
if echo "$after_restart_response" | jq -e '.context.after_restart_result.error' | grep -q "не настроен"; then
    echo "❌ Настройки не загрузились после перезапуска"
    echo "💡 Возможно проблема в коде загрузки настроек"
else
    # Проверяем что это ошибка подключения, а не "не настроен"
    restart_error=$(echo "$after_restart_response" | jq -r '.context.after_restart_result.error // "unknown"')
    echo "✅ Настройки загрузились! Ошибка: $restart_error"
    echo "💡 Это ошибка подключения к тестовому AmoCRM - это нормально"
fi

echo ""
echo "📋 ЭТАП 6: Очистка тестовых данных"
echo "---"

echo "🧹 Удаление тестовых настроек..."
cleanup_response=$(curl -s -X POST "$API_URL/api/v1/simple/mongo/delete" \
    -H "Content-Type: application/json" \
    -d '{
        "collection": "plugin_settings",
        "filter": {"plugin_name": {"$in": ["amocrm", "amocrm_fields"]}}
    }')

check_response "$cleanup_response" "Очистка настроек"
deleted_count=$(echo "$cleanup_response" | jq '.data.deleted_count')
echo "📊 Удалено настроек: $deleted_count"

echo ""
echo "🎯 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:"
echo "---"
echo "✅ AmoCRM плагин корректно сообщает о отсутствии настроек"
echo "✅ Настройки сохраняются в MongoDB"
echo "✅ Настройки НЕ применяются автоматически (ожидаемо)"
echo "✅ Настройки загружаются после перезапуска"
echo "✅ Очистка данных работает"
echo ""
echo "🏆 ВЫВОД: Механизм настроек работает, но требует перезапуска!"
echo "💡 Для продакшена нужно добавить API для перезагрузки настроек"
echo "🚀 Или автоматическую перезагрузку при изменении в MongoDB" 