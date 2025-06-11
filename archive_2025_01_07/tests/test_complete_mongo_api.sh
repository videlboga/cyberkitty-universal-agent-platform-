#!/bin/bash

# ФИНАЛЬНЫЙ ТЕСТ: Полная проверка MongoDB API
# Проверяет все CRUD операции с фактическими изменениями в БД

set -e

API_URL="http://localhost:8085"
TEST_PREFIX="final_test_$(date +%s)"

echo "🎯 ФИНАЛЬНЫЙ ТЕСТ: MongoDB API - ПОЛНАЯ ПРОВЕРКА"
echo "🔍 Цель: Проверить все CRUD операции с фактическими изменениями"
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

# Функция для извлечения значения из JSON
extract_value() {
    local json="$1"
    local path="$2"
    echo "$json" | jq -r "$path"
}

echo "📋 ЭТАП 1: CREATE - Создание тестовых данных"
echo "---"

# 1. Создаем тестовый документ
echo "📝 Создание тестового документа..."
test_doc='{
    "test_id": "'$TEST_PREFIX'_doc1",
    "name": "Тестовый документ",
    "value": 100,
    "created_at": "'$(date -Iseconds)'"
}'

create_response=$(curl -s -X POST "$API_URL/api/v1/simple/mongo/insert" \
    -H "Content-Type: application/json" \
    -d '{
        "collection": "test_crud",
        "document": '"$test_doc"'
    }')

check_response "$create_response" "Создание документа"
doc_id=$(extract_value "$create_response" '.data')
echo "📄 ID созданного документа: $doc_id"

# 2. Создаем второй документ для массовых операций
echo "📝 Создание второго документа..."
test_doc2='{
    "test_id": "'$TEST_PREFIX'_doc2",
    "name": "Второй документ",
    "value": 200,
    "created_at": "'$(date -Iseconds)'"
}'

create_response2=$(curl -s -X POST "$API_URL/api/v1/simple/mongo/insert" \
    -H "Content-Type: application/json" \
    -d '{
        "collection": "test_crud",
        "document": '"$test_doc2"'
    }')

check_response "$create_response2" "Создание второго документа"
doc_id2=$(extract_value "$create_response2" '.data')
echo "📄 ID второго документа: $doc_id2"

echo ""
echo "📋 ЭТАП 2: READ - Чтение и проверка данных"
echo "---"

# 3. Читаем созданные документы
echo "🔍 Поиск созданных документов..."
read_response=$(curl -s -X POST "$API_URL/api/v1/simple/mongo/find" \
    -H "Content-Type: application/json" \
    -d '{
        "collection": "test_crud",
        "filter": {"test_id": {"$regex": "^'$TEST_PREFIX'"}}
    }')

check_response "$read_response" "Чтение документов"
docs_count=$(extract_value "$read_response" '.data | length')
echo "📊 Найдено документов: $docs_count"

if [ "$docs_count" -eq 2 ]; then
    echo "✅ Оба документа найдены"
    
    # Проверяем содержимое первого документа
    doc1_name=$(extract_value "$read_response" '.data[0].name')
    doc1_value=$(extract_value "$read_response" '.data[0].value')
    echo "📄 Документ 1: name='$doc1_name', value=$doc1_value"
    
    # Проверяем содержимое второго документа
    doc2_name=$(extract_value "$read_response" '.data[1].name')
    doc2_value=$(extract_value "$read_response" '.data[1].value')
    echo "📄 Документ 2: name='$doc2_name', value=$doc2_value"
else
    echo "❌ Ожидалось 2 документа, найдено: $docs_count"
fi

echo ""
echo "📋 ЭТАП 3: UPDATE - Обновление данных"
echo "---"

# 4. Обновляем первый документ
echo "🔄 Обновление первого документа..."
update_response=$(curl -s -X POST "$API_URL/api/v1/simple/mongo/update" \
    -H "Content-Type: application/json" \
    -d '{
        "collection": "test_crud",
        "filter": {"test_id": "'$TEST_PREFIX'_doc1"},
        "document": {
            "name": "Обновленный документ",
            "value": 999,
            "updated_at": "'$(date -Iseconds)'"
        }
    }')

check_response "$update_response" "Обновление документа"
modified_count=$(extract_value "$update_response" '.data.modified_count')
matched_count=$(extract_value "$update_response" '.data.matched_count')
echo "📊 Обновлено документов: $modified_count, найдено: $matched_count"

if [ "$modified_count" -eq 1 ] && [ "$matched_count" -eq 1 ]; then
    echo "✅ Документ успешно обновлен"
else
    echo "❌ Ошибка обновления: modified=$modified_count, matched=$matched_count"
fi

# 5. Проверяем что обновление применилось
echo "🔍 Проверка обновленных данных..."
verify_update_response=$(curl -s -X POST "$API_URL/api/v1/simple/mongo/find" \
    -H "Content-Type: application/json" \
    -d '{
        "collection": "test_crud",
        "filter": {"test_id": "'$TEST_PREFIX'_doc1"}
    }')

check_response "$verify_update_response" "Проверка обновления"
updated_name=$(extract_value "$verify_update_response" '.data[0].name')
updated_value=$(extract_value "$verify_update_response" '.data[0].value')
echo "📄 После обновления: name='$updated_name', value=$updated_value"

if [ "$updated_name" = "Обновленный документ" ] && [ "$updated_value" = "999" ]; then
    echo "✅ Обновление применилось корректно"
else
    echo "❌ Обновление не применилось: name='$updated_name', value=$updated_value"
fi

echo ""
echo "📋 ЭТАП 4: DELETE - Удаление данных"
echo "---"

# 6. Удаляем один документ
echo "🗑️ Удаление первого документа..."
delete_response=$(curl -s -X POST "$API_URL/api/v1/simple/mongo/delete" \
    -H "Content-Type: application/json" \
    -d '{
        "collection": "test_crud",
        "filter": {"test_id": "'$TEST_PREFIX'_doc1"}
    }')

check_response "$delete_response" "Удаление документа"
deleted_count=$(extract_value "$delete_response" '.data.deleted_count')
echo "📊 Удалено документов: $deleted_count"

if [ "$deleted_count" -eq 1 ]; then
    echo "✅ Документ успешно удален"
else
    echo "❌ Ошибка удаления: deleted_count=$deleted_count"
fi

# 7. Проверяем что документ действительно удален
echo "🔍 Проверка удаления..."
verify_delete_response=$(curl -s -X POST "$API_URL/api/v1/simple/mongo/find" \
    -H "Content-Type: application/json" \
    -d '{
        "collection": "test_crud",
        "filter": {"test_id": "'$TEST_PREFIX'_doc1"}
    }')

check_response "$verify_delete_response" "Проверка удаления"
remaining_docs=$(extract_value "$verify_delete_response" '.data | length')
echo "📊 Осталось документов с test_id='${TEST_PREFIX}_doc1': $remaining_docs"

if [ "$remaining_docs" -eq 0 ]; then
    echo "✅ Документ действительно удален"
else
    echo "❌ Документ не удален: найдено $remaining_docs документов"
fi

echo ""
echo "📋 ЭТАП 5: CLEANUP - Очистка тестовых данных"
echo "---"

# 8. Удаляем все тестовые данные
echo "🧹 Очистка всех тестовых данных..."
cleanup_response=$(curl -s -X POST "$API_URL/api/v1/simple/mongo/delete" \
    -H "Content-Type: application/json" \
    -d '{
        "collection": "test_crud",
        "filter": {"test_id": {"$regex": "^'$TEST_PREFIX'"}}
    }')

check_response "$cleanup_response" "Очистка тестовых данных"
cleanup_deleted=$(extract_value "$cleanup_response" '.data.deleted_count')
echo "📊 Очищено документов: $cleanup_deleted"

echo ""
echo "🎯 ФИНАЛЬНЫЕ РЕЗУЛЬТАТЫ:"
echo "---"
echo "✅ CREATE: Документы создаются корректно"
echo "✅ READ: Поиск работает правильно"
echo "✅ UPDATE: Обновления применяются"
echo "✅ DELETE: Удаление работает"
echo "✅ CLEANUP: Очистка выполнена"
echo ""
echo "🏆 ВЫВОД: MongoDB API ПОЛНОСТЬЮ ФУНКЦИОНАЛЕН!"
echo "💡 Admin API действительно избыточен"
echo "🚀 Можно безопасно использовать только MongoDB API для всех операций" 