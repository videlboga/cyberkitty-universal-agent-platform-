#!/usr/bin/env python3
"""
Тест реальных операций MongoDB плагина
Проверяет фактические изменения в базе данных
"""

import asyncio
import pytest
from datetime import datetime
from typing import Dict, Any

from app.core.simple_engine import SimpleScenarioEngine
from app.plugins.mongo_plugin import MongoPlugin


class TestMongoRealOperations:
    """Тесты реальных операций с MongoDB"""
    
    @pytest.fixture
    async def engine_with_mongo(self):
        """Создает движок с MongoDB плагином"""
        engine = SimpleScenarioEngine()
        mongo_plugin = MongoPlugin()
        
        # Инициализируем плагин
        await mongo_plugin.initialize()
        engine.register_plugin(mongo_plugin)
        
        return engine, mongo_plugin
    
    @pytest.mark.asyncio
    async def test_mongo_crud_operations(self, engine_with_mongo):
        """Тест полного CRUD цикла с проверкой фактических изменений"""
        engine, mongo_plugin = engine_with_mongo
        
        # Проверяем подключение
        health = await mongo_plugin.healthcheck()
        if not health:
            pytest.skip("MongoDB недоступен")
        
        test_collection = "test_crud_operations"
        test_doc_id = f"test_doc_{datetime.now().timestamp()}"
        
        try:
            # === 1. CREATE - Создание документа ===
            print("🔄 Тестируем CREATE операцию...")
            
            create_scenario = {
                "scenario_id": "test_create",
                "steps": [
                    {
                        "id": "create_doc",
                        "type": "mongo_insert_one",
                        "params": {
                            "collection": test_collection,
                            "document": {
                                "_id": test_doc_id,
                                "name": "Test Document",
                                "value": 100,
                                "created_at": datetime.now().isoformat(),
                                "tags": ["test", "crud"]
                            },
                            "output_var": "create_result"
                        }
                    }
                ]
            }
            
            context = {}
            result = await engine.execute_scenario(create_scenario, context)
            
            # Проверяем результат создания
            create_result = context.get("create_result", {})
            assert create_result.get("success") == True, f"Создание не удалось: {create_result}"
            assert create_result.get("inserted_id") == test_doc_id
            
            print(f"✅ CREATE: Документ {test_doc_id} создан")
            
            # === 2. READ - Чтение документа ===
            print("🔄 Тестируем READ операцию...")
            
            read_scenario = {
                "scenario_id": "test_read",
                "steps": [
                    {
                        "id": "read_doc",
                        "type": "mongo_find_one",
                        "params": {
                            "collection": test_collection,
                            "filter": {"_id": test_doc_id},
                            "output_var": "read_result"
                        }
                    }
                ]
            }
            
            context = {}
            result = await engine.execute_scenario(read_scenario, context)
            
            # Проверяем результат чтения
            read_result = context.get("read_result", {})
            assert read_result.get("success") == True, f"Чтение не удалось: {read_result}"
            
            document = read_result.get("document")
            assert document is not None, "Документ не найден"
            assert document.get("_id") == test_doc_id
            assert document.get("name") == "Test Document"
            assert document.get("value") == 100
            
            print(f"✅ READ: Документ {test_doc_id} прочитан корректно")
            
            # === 3. UPDATE - Обновление документа ===
            print("🔄 Тестируем UPDATE операцию...")
            
            update_scenario = {
                "scenario_id": "test_update",
                "steps": [
                    {
                        "id": "update_doc",
                        "type": "mongo_update_one",
                        "params": {
                            "collection": test_collection,
                            "filter": {"_id": test_doc_id},
                            "update": {
                                "$set": {
                                    "name": "Updated Test Document",
                                    "value": 200,
                                    "updated_at": datetime.now().isoformat()
                                },
                                "$push": {
                                    "tags": "updated"
                                }
                            },
                            "output_var": "update_result"
                        }
                    }
                ]
            }
            
            context = {}
            result = await engine.execute_scenario(update_scenario, context)
            
            # Проверяем результат обновления
            update_result = context.get("update_result", {})
            assert update_result.get("success") == True, f"Обновление не удалось: {update_result}"
            assert update_result.get("modified_count") == 1
            
            print(f"✅ UPDATE: Документ {test_doc_id} обновлен")
            
            # === 4. VERIFY UPDATE - Проверяем что изменения применились ===
            print("🔄 Проверяем фактические изменения...")
            
            context = {}
            result = await engine.execute_scenario(read_scenario, context)
            
            read_result = context.get("read_result", {})
            updated_document = read_result.get("document")
            
            assert updated_document.get("name") == "Updated Test Document", "Имя не обновилось"
            assert updated_document.get("value") == 200, "Значение не обновилось"
            assert "updated" in updated_document.get("tags", []), "Тег не добавился"
            assert "updated_at" in updated_document, "Поле updated_at не добавилось"
            
            print("✅ VERIFY: Все изменения применились корректно")
            
            # === 5. DELETE - Удаление документа ===
            print("🔄 Тестируем DELETE операцию...")
            
            delete_scenario = {
                "scenario_id": "test_delete",
                "steps": [
                    {
                        "id": "delete_doc",
                        "type": "mongo_delete_one",
                        "params": {
                            "collection": test_collection,
                            "filter": {"_id": test_doc_id},
                            "output_var": "delete_result"
                        }
                    }
                ]
            }
            
            context = {}
            result = await engine.execute_scenario(delete_scenario, context)
            
            # Проверяем результат удаления
            delete_result = context.get("delete_result", {})
            assert delete_result.get("success") == True, f"Удаление не удалось: {delete_result}"
            assert delete_result.get("deleted_count") == 1
            
            print(f"✅ DELETE: Документ {test_doc_id} удален")
            
            # === 6. VERIFY DELETE - Проверяем что документ действительно удален ===
            print("🔄 Проверяем что документ действительно удален...")
            
            context = {}
            result = await engine.execute_scenario(read_scenario, context)
            
            read_result = context.get("read_result", {})
            assert read_result.get("success") == True, "Запрос должен быть успешным"
            assert read_result.get("document") is None, "Документ должен быть удален"
            
            print("✅ VERIFY DELETE: Документ действительно удален")
            
        except Exception as e:
            print(f"❌ Ошибка в тесте: {e}")
            raise
        
        finally:
            # Очистка - удаляем тестовый документ если он остался
            try:
                await mongo_plugin._delete_one(test_collection, {"_id": test_doc_id})
            except:
                pass
    
    @pytest.mark.asyncio
    async def test_mongo_bulk_operations(self, engine_with_mongo):
        """Тест массовых операций с проверкой количества изменений"""
        engine, mongo_plugin = engine_with_mongo
        
        # Проверяем подключение
        health = await mongo_plugin.healthcheck()
        if not health:
            pytest.skip("MongoDB недоступен")
        
        test_collection = "test_bulk_operations"
        test_prefix = f"bulk_test_{datetime.now().timestamp()}"
        
        try:
            # === 1. BULK INSERT - Массовая вставка ===
            print("🔄 Тестируем массовую вставку...")
            
            documents = [
                {"_id": f"{test_prefix}_{i}", "name": f"Document {i}", "value": i * 10}
                for i in range(1, 6)
            ]
            
            bulk_insert_scenario = {
                "scenario_id": "test_bulk_insert",
                "steps": [
                    {
                        "id": "bulk_insert",
                        "type": "mongo_insert_many",
                        "params": {
                            "collection": test_collection,
                            "documents": documents,
                            "output_var": "bulk_insert_result"
                        }
                    }
                ]
            }
            
            context = {}
            result = await engine.execute_scenario(bulk_insert_scenario, context)
            
            # Проверяем результат массовой вставки
            bulk_result = context.get("bulk_insert_result", {})
            assert bulk_result.get("success") == True, f"Массовая вставка не удалась: {bulk_result}"
            assert bulk_result.get("inserted_count") == 5
            assert len(bulk_result.get("inserted_ids", [])) == 5
            
            print("✅ BULK INSERT: 5 документов вставлено")
            
            # === 2. BULK UPDATE - Массовое обновление ===
            print("🔄 Тестируем массовое обновление...")
            
            bulk_update_scenario = {
                "scenario_id": "test_bulk_update",
                "steps": [
                    {
                        "id": "bulk_update",
                        "type": "mongo_update_many",
                        "params": {
                            "collection": test_collection,
                            "filter": {"_id": {"$regex": f"^{test_prefix}"}},
                            "update": {
                                "$set": {"updated": True, "batch": test_prefix},
                                "$inc": {"value": 100}
                            },
                            "output_var": "bulk_update_result"
                        }
                    }
                ]
            }
            
            context = {}
            result = await engine.execute_scenario(bulk_update_scenario, context)
            
            # Проверяем результат массового обновления
            update_result = context.get("bulk_update_result", {})
            assert update_result.get("success") == True, f"Массовое обновление не удалось: {update_result}"
            assert update_result.get("modified_count") == 5
            
            print("✅ BULK UPDATE: 5 документов обновлено")
            
            # === 3. VERIFY BULK CHANGES - Проверяем изменения ===
            print("🔄 Проверяем массовые изменения...")
            
            find_many_scenario = {
                "scenario_id": "test_find_many",
                "steps": [
                    {
                        "id": "find_updated",
                        "type": "mongo_find_many",
                        "params": {
                            "collection": test_collection,
                            "filter": {"_id": {"$regex": f"^{test_prefix}"}},
                            "output_var": "find_result"
                        }
                    }
                ]
            }
            
            context = {}
            result = await engine.execute_scenario(find_many_scenario, context)
            
            find_result = context.get("find_result", {})
            assert find_result.get("success") == True
            
            documents = find_result.get("documents", [])
            assert len(documents) == 5, f"Найдено {len(documents)} документов вместо 5"
            
            # Проверяем что все документы обновились
            for doc in documents:
                assert doc.get("updated") == True, f"Документ {doc.get('_id')} не обновился"
                assert doc.get("batch") == test_prefix, f"Batch не установился для {doc.get('_id')}"
                # Проверяем что value увеличился на 100
                original_value = int(doc.get("_id").split("_")[-1]) * 10
                assert doc.get("value") == original_value + 100, f"Value не увеличился для {doc.get('_id')}"
            
            print("✅ VERIFY BULK: Все массовые изменения применились")
            
            # === 4. BULK DELETE - Массовое удаление ===
            print("🔄 Тестируем массовое удаление...")
            
            bulk_delete_scenario = {
                "scenario_id": "test_bulk_delete",
                "steps": [
                    {
                        "id": "bulk_delete",
                        "type": "mongo_delete_many",
                        "params": {
                            "collection": test_collection,
                            "filter": {"_id": {"$regex": f"^{test_prefix}"}},
                            "output_var": "bulk_delete_result"
                        }
                    }
                ]
            }
            
            context = {}
            result = await engine.execute_scenario(bulk_delete_scenario, context)
            
            # Проверяем результат массового удаления
            delete_result = context.get("bulk_delete_result", {})
            assert delete_result.get("success") == True, f"Массовое удаление не удалось: {delete_result}"
            assert delete_result.get("deleted_count") == 5
            
            print("✅ BULK DELETE: 5 документов удалено")
            
            # === 5. VERIFY BULK DELETE ===
            print("🔄 Проверяем что все документы удалены...")
            
            context = {}
            result = await engine.execute_scenario(find_many_scenario, context)
            
            find_result = context.get("find_result", {})
            documents = find_result.get("documents", [])
            assert len(documents) == 0, f"Найдено {len(documents)} документов, должно быть 0"
            
            print("✅ VERIFY BULK DELETE: Все документы удалены")
            
        except Exception as e:
            print(f"❌ Ошибка в тесте массовых операций: {e}")
            raise
        
        finally:
            # Очистка
            try:
                await mongo_plugin._delete_many(test_collection, {"_id": {"$regex": f"^{test_prefix}"}})
            except:
                pass


if __name__ == "__main__":
    async def run_tests():
        """Запуск тестов"""
        print("🚀 Запуск тестов MongoDB операций...")
        
        test_instance = TestMongoRealOperations()
        
        # Создаем движок с MongoDB
        engine = SimpleScenarioEngine()
        mongo_plugin = MongoPlugin()
        
        try:
            await mongo_plugin.initialize()
            engine.register_plugin(mongo_plugin)
            
            print("\n=== ТЕСТ CRUD ОПЕРАЦИЙ ===")
            await test_instance.test_mongo_crud_operations((engine, mongo_plugin))
            
            print("\n=== ТЕСТ МАССОВЫХ ОПЕРАЦИЙ ===")
            await test_instance.test_mongo_bulk_operations((engine, mongo_plugin))
            
            print("\n✅ Все тесты MongoDB прошли успешно!")
            
        except Exception as e:
            print(f"\n❌ Тесты не прошли: {e}")
            raise
    
    asyncio.run(run_tests()) 