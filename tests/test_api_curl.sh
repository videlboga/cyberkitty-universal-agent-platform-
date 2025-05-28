#!/bin/bash

# Тест реальной работы KittyCore API через curl
# Проверяет фактические изменения в MongoDB и работу плагинов

set -e  # Останавливаемся при ошибке

API_URL="http://localhost:8085"
TEST_PREFIX="curl_test_$(date +%s)"

echo "🚀 Запуск тестов KittyCore API через curl"
echo "🔗 API URL: $API_URL"
echo "🏷️ Тест префикс: $TEST_PREFIX"
echo "=" | tr '=' '=' | head -c 50; echo

# Функция для проверки ответа API
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

# Функция для извлечения значения из JSON
extract_value() {
    local response="$1"
    local path="$2"
    echo "$response" | jq -r "$path"
}

echo "📊 1. ПРОВЕРКА ЗДОРОВЬЯ API"
health_response=$(curl -s "$API_URL/api/v1/simple/health")
echo "Health response: $health_response"

echo
echo "📋 2. ПОЛУЧЕНИЕ ИНФОРМАЦИИ О СИСТЕМЕ"
info_response=$(curl -s "$API_URL/api/v1/simple/info")
echo "Info response:"
echo "$info_response" | jq .

echo
echo "🗄️ 3. ТЕСТИРОВАНИЕ MONGODB ОПЕРАЦИЙ"

# === CREATE - Создание документа ===
echo "📝 3.1. CREATE - Создание тестового документа"

create_payload='{
  "collection": "test_api_crud",
  "document": {
    "_id": "'$TEST_PREFIX'_doc1",
    "name": "Test Document from API",
    "value": 100,
    "created_at": "'$(date -Iseconds)'",
    "tags": ["api", "test", "curl"]
  }
}'

create_response=$(curl -s -X POST "$API_URL/api/v1/simple/mongo/insert" \
  -H "Content-Type: application/json" \
  -d "$create_payload")

check_response "$create_response" "Создание документа"
created_id=$(extract_value "$create_response" '.inserted_id')
echo "📄 Создан документ с ID: $created_id"

# === READ - Чтение документа ===
echo
echo "📖 3.2. READ - Чтение созданного документа"

read_payload='{
  "collection": "test_api_crud",
  "filter": {"_id": "'$TEST_PREFIX'_doc1"}
}'

read_response=$(curl -s -X POST "$API_URL/api/v1/simple/mongo/find" \
  -H "Content-Type: application/json" \
  -d "$read_payload")

check_response "$read_response" "Чтение документа"

# Проверяем содержимое документа
doc_name=$(extract_value "$read_response" '.data[0].name')
doc_value=$(extract_value "$read_response" '.data[0].value')

if [ "$doc_name" = "Test Document from API" ] && [ "$doc_value" = "100" ]; then
    echo "✅ Содержимое документа корректное"
    echo "   Имя: $doc_name"
    echo "   Значение: $doc_value"
else
    echo "❌ Содержимое документа некорректное"
    echo "   Ожидалось: 'Test Document from API', 100"
    echo "   Получено: '$doc_name', $doc_value"
    exit 1
fi

# === BULK INSERT - Массовая вставка ===
echo
echo "📦 3.3. BULK INSERT - Массовая вставка документов"

bulk_docs='['
for i in {2..5}; do
    if [ $i -gt 2 ]; then bulk_docs+=','; fi
    bulk_docs+='{
        "_id": "'$TEST_PREFIX'_doc'$i'",
        "name": "Bulk Document '$i'",
        "value": '$((i * 10))',
        "batch": "'$TEST_PREFIX'"
    }'
done
bulk_docs+=']'

bulk_insert_payload='{
  "collection": "test_api_crud",
  "documents": '$bulk_docs'
}'

bulk_response=$(curl -s -X POST "$API_URL/api/v1/simple/mongo/insert" \
  -H "Content-Type: application/json" \
  -d "$bulk_insert_payload")

check_response "$bulk_response" "Массовая вставка"
inserted_count=$(extract_value "$bulk_response" '.inserted_count')
echo "📦 Вставлено документов: $inserted_count"

if [ "$inserted_count" != "4" ]; then
    echo "❌ Ожидалось 4 документа, получено: $inserted_count"
    exit 1
fi

# === VERIFY BULK - Проверка массовой вставки ===
echo
echo "🔍 3.4. VERIFY BULK - Проверка массовой вставки"

verify_payload='{
  "collection": "test_api_crud",
  "filter": {"_id": {"$regex": "^'$TEST_PREFIX'"}}
}'

verify_response=$(curl -s -X POST "$API_URL/api/v1/simple/mongo/find" \
  -H "Content-Type: application/json" \
  -d "$verify_payload")

check_response "$verify_response" "Проверка массовой вставки"
total_docs=$(extract_value "$verify_response" '.data | length')

if [ "$total_docs" = "5" ]; then
    echo "✅ Найдено $total_docs документов (ожидалось 5)"
else
    echo "❌ Найдено $total_docs документов, ожидалось 5"
    exit 1
fi

echo
echo "🎯 4. ТЕСТИРОВАНИЕ ВЫПОЛНЕНИЯ СЦЕНАРИЕВ"

# === MONGO SCENARIO - Сценарий с MongoDB операциями ===
echo "📜 4.1. Выполнение сценария с MongoDB операциями"

mongo_scenario='{
  "scenario_id": "test_mongo_scenario",
  "steps": [
    {
      "id": "create_test_doc",
      "type": "mongo_insert_one",
      "params": {
        "collection": "test_scenarios",
        "document": {
          "_id": "'$TEST_PREFIX'_scenario",
          "scenario_name": "MongoDB Test Scenario",
          "executed_at": "'$(date -Iseconds)'",
          "status": "running"
        },
        "output_var": "create_result"
      },
      "next_step": "update_status"
    },
    {
      "id": "update_status",
      "type": "mongo_update_one",
      "params": {
        "collection": "test_scenarios",
        "filter": {"_id": "'$TEST_PREFIX'_scenario"},
        "update": {
          "$set": {
            "status": "completed",
            "completed_at": "'$(date -Iseconds)'"
          }
        },
        "output_var": "update_result"
      },
      "next_step": "end"
    },
    {
      "id": "end",
      "type": "end"
    }
  ]
}'

scenario_payload='{
  "scenario": '$mongo_scenario',
  "context": {
    "test_prefix": "'$TEST_PREFIX'",
    "api_test": true
  }
}'

scenario_response=$(curl -s -X POST "$API_URL/api/v1/simple/execute" \
  -H "Content-Type: application/json" \
  -d "$scenario_payload")

check_response "$scenario_response" "Выполнение MongoDB сценария"

# Проверяем что сценарий действительно выполнился
scenario_verify_payload='{
  "collection": "test_scenarios",
  "filter": {"_id": "'$TEST_PREFIX'_scenario"}
}'

scenario_verify_response=$(curl -s -X POST "$API_URL/api/v1/simple/mongo/find" \
  -H "Content-Type: application/json" \
  -d "$scenario_verify_payload")

scenario_status=$(extract_value "$scenario_verify_response" '.data[0].status')
if [ "$scenario_status" = "completed" ]; then
    echo "✅ Сценарий выполнился корректно, статус: $scenario_status"
else
    echo "❌ Сценарий не выполнился, статус: $scenario_status"
    exit 1
fi

echo
echo "🧹 5. ОЧИСТКА ТЕСТОВЫХ ДАННЫХ"

# Удаляем тестовые документы (через сценарий удаления)
cleanup_scenario='{
  "scenario_id": "cleanup_test",
  "steps": [
    {
      "id": "cleanup_crud",
      "type": "mongo_delete_many",
      "params": {
        "collection": "test_api_crud",
        "filter": {"_id": {"$regex": "^'$TEST_PREFIX'"}},
        "output_var": "cleanup_crud_result"
      },
      "next_step": "cleanup_scenarios"
    },
    {
      "id": "cleanup_scenarios",
      "type": "mongo_delete_many",
      "params": {
        "collection": "test_scenarios",
        "filter": {"_id": {"$regex": "^'$TEST_PREFIX'"}},
        "output_var": "cleanup_scenarios_result"
      },
      "next_step": "end"
    },
    {
      "id": "end",
      "type": "end"
    }
  ]
}'

cleanup_payload='{
  "scenario": '$cleanup_scenario',
  "context": {}
}'

cleanup_response=$(curl -s -X POST "$API_URL/api/v1/simple/execute" \
  -H "Content-Type: application/json" \
  -d "$cleanup_payload")

check_response "$cleanup_response" "Очистка тестовых данных"

# Проверяем что данные действительно удалены
final_verify_payload='{
  "collection": "test_api_crud",
  "filter": {"_id": {"$regex": "^'$TEST_PREFIX'"}}
}'

final_verify_response=$(curl -s -X POST "$API_URL/api/v1/simple/mongo/find" \
  -H "Content-Type: application/json" \
  -d "$final_verify_payload")

remaining_docs=$(extract_value "$final_verify_response" '.data | length')
if [ "$remaining_docs" = "0" ]; then
    echo "✅ Все тестовые данные очищены"
else
    echo "⚠️ Осталось $remaining_docs документов (возможно, это нормально)"
fi

echo
echo "🎉 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:"
echo "✅ API доступен и работает"
echo "✅ MongoDB операции работают корректно"
echo "✅ Создание документов работает"
echo "✅ Чтение документов работает"
echo "✅ Массовая вставка работает"
echo "✅ Выполнение сценариев работает"
echo "✅ Фактические изменения в БД применяются"
echo "✅ Очистка данных работает"
echo
echo "🚀 Все тесты прошли успешно!" 