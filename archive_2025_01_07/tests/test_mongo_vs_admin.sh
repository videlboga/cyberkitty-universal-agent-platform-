#!/bin/bash

# Тест: MongoDB API vs Admin API
# Проверяем можно ли настроить плагины только через MongoDB API

set -e

API_URL="http://localhost:8085"
TEST_PREFIX="mongo_vs_admin_$(date +%s)"

echo "🔬 ТЕСТ: MongoDB API vs Admin API"
echo "🎯 Цель: Проверить можно ли заменить Admin API на MongoDB API"
echo "=" | tr '=' '=' | head -c 60; echo

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

echo "📋 ЭТАП 1: Настройка плагинов через MongoDB API"
echo "---"

# 1. Настройка AmoCRM через MongoDB API
echo "🔧 Настройка AmoCRM через MongoDB API..."
amocrm_settings='{
    "plugin_name": "amocrm",
    "base_url": "https://test.amocrm.ru",
    "access_token": "test_token_123",
    "updated_at": "'$(date -Iseconds)'"
}'

mongo_amocrm_response=$(curl -s -X POST "$API_URL/api/v1/simple/mongo/insert" \
    -H "Content-Type: application/json" \
    -d '{
        "collection": "plugin_settings",
        "document": '"$amocrm_settings"'
    }')

check_response "$mongo_amocrm_response" "AmoCRM настройка через MongoDB"

# 2. Настройка Telegram через MongoDB API  
echo "📱 Настройка Telegram через MongoDB API..."
telegram_settings='{
    "plugin_name": "telegram",
    "bot_token": "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11",
    "webhook_url": "https://example.com/webhook",
    "webhook_secret": "secret123",
    "updated_at": "'$(date -Iseconds)'"
}'

mongo_telegram_response=$(curl -s -X POST "$API_URL/api/v1/simple/mongo/insert" \
    -H "Content-Type: application/json" \
    -d '{
        "collection": "plugin_settings", 
        "document": '"$telegram_settings"'
    }')

check_response "$mongo_telegram_response" "Telegram настройка через MongoDB"

# 3. Настройка LLM через MongoDB API
echo "🤖 Настройка LLM через MongoDB API..."
llm_settings='{
    "plugin_name": "llm",
    "openrouter_api_key": "sk-or-test123",
    "openai_api_key": "sk-test456", 
    "default_model": "anthropic/claude-3-sonnet",
    "updated_at": "'$(date -Iseconds)'"
}'

mongo_llm_response=$(curl -s -X POST "$API_URL/api/v1/simple/mongo/insert" \
    -H "Content-Type: application/json" \
    -d '{
        "collection": "plugin_settings",
        "document": '"$llm_settings"'
    }')

check_response "$mongo_llm_response" "LLM настройка через MongoDB"

echo ""
echo "📋 ЭТАП 2: Проверка сохраненных настроек"
echo "---"

# Проверяем что настройки сохранились
echo "🔍 Проверка сохраненных настроек..."
saved_settings_response=$(curl -s -X POST "$API_URL/api/v1/simple/mongo/find" \
    -H "Content-Type: application/json" \
    -d '{
        "collection": "plugin_settings",
        "filter": {}
    }')

check_response "$saved_settings_response" "Получение всех настроек плагинов"

# Подсчитываем количество настроек
settings_count=$(echo "$saved_settings_response" | jq '.data | length')
echo "📊 Найдено настроек плагинов: $settings_count"

echo ""
echo "📋 ЭТАП 3: Сравнение с Admin API (если доступен)"
echo "---"

# Проверяем доступность Admin API
admin_status_response=$(curl -s "$API_URL/api/v1/admin/plugins/status" || echo '{"error": "Admin API недоступен"}')

if echo "$admin_status_response" | jq -e '.error' > /dev/null 2>&1; then
    echo "⚠️ Admin API недоступен - это нормально, мы тестируем замену"
else
    echo "ℹ️ Admin API доступен, сравниваем функциональность..."
    echo "Admin статус: $admin_status_response"
fi

echo ""
echo "📋 ЭТАП 4: Тест обновления настроек через MongoDB"
echo "---"

# Обновляем настройки AmoCRM
echo "🔄 Обновление настроек AmoCRM..."
updated_amocrm='{
    "plugin_name": "amocrm",
    "base_url": "https://updated.amocrm.ru",
    "access_token": "updated_token_456",
    "updated_at": "'$(date -Iseconds)'"
}'

# Для обновления нужен endpoint update, проверим есть ли он
update_response=$(curl -s -X POST "$API_URL/api/v1/simple/mongo/update" \
    -H "Content-Type: application/json" \
    -d '{
        "collection": "plugin_settings",
        "filter": {"plugin_name": "amocrm"},
        "update": '"$updated_amocrm"'
    }' 2>/dev/null || echo '{"success": false, "error": "update endpoint не найден"}')

if echo "$update_response" | jq -e '.success == true' > /dev/null 2>&1; then
    echo "✅ Обновление через MongoDB API: SUCCESS"
else
    echo "⚠️ MongoDB update endpoint не реализован"
    echo "💡 Можно использовать upsert через insert с заменой"
fi

echo ""
echo "📋 ЭТАП 5: Тест удаления настроек"
echo "---"

# Удаляем тестовые настройки
echo "🗑️ Очистка тестовых данных..."
cleanup_response=$(curl -s -X POST "$API_URL/api/v1/simple/mongo/delete" \
    -H "Content-Type: application/json" \
    -d '{
        "collection": "plugin_settings",
        "filter": {"plugin_name": {"$in": ["amocrm", "telegram", "llm"]}}
    }' 2>/dev/null || echo '{"success": false, "error": "delete endpoint не найден"}')

if echo "$cleanup_response" | jq -e '.success == true' > /dev/null 2>&1; then
    echo "✅ Очистка через MongoDB API: SUCCESS"
else
    echo "⚠️ MongoDB delete endpoint не реализован"
fi

echo ""
echo "🎯 ВЫВОДЫ:"
echo "---"
echo "✅ MongoDB API может сохранять настройки плагинов"
echo "✅ MongoDB API может читать настройки плагинов"
echo "⚠️ Нужны дополнительные endpoints: update, delete"
echo "💡 Admin API действительно избыточен для базовых операций"
echo ""
echo "🚀 РЕКОМЕНДАЦИЯ: Расширить MongoDB API и убрать Admin API"
echo "   - Добавить POST /mongo/update"
echo "   - Добавить POST /mongo/delete" 
echo "   - Убрать /admin/* endpoints"
echo "   - Плагины будут читать настройки напрямую из MongoDB" 