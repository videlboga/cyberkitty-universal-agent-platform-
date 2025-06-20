"""
🧪 Тесты DatabaseTool

Тестирование универсального инструмента для работы с базами данных.
Часть 1: SQLite функционал
"""

import pytest
import asyncio
import tempfile
import os
from pathlib import Path

from kittycore.tools.database_tool import (
    DatabaseTool,
    DatabaseConnection,
    create_database_tool,
    create_sqlite_tool
)

class TestDatabaseConnection:
    """Тесты конфигурации подключения"""
    
    def test_sqlite_config(self):
        """Тест конфигурации SQLite"""
        config = DatabaseConnection(db_type='sqlite', database='test.db')
        assert config.db_type == 'sqlite'
        assert config.database == 'test.db'
    
    def test_postgresql_config(self):
        """Тест конфигурации PostgreSQL"""
        config = DatabaseConnection(
            db_type='postgresql',
            host='localhost',
            database='testdb',
            username='user',
            password='pass'
        )
        assert config.db_type == 'postgresql'
        assert config.host == 'localhost'
        assert config.database == 'testdb'
    
    def test_invalid_config(self):
        """Тест невалидной конфигурации"""
        with pytest.raises(ValueError):
            DatabaseConnection(db_type='postgresql')  # Без host и database

@pytest.mark.asyncio
class TestDatabaseTool:
    """Тесты DatabaseTool"""
    
    @pytest.fixture
    async def temp_db_file(self):
        """Временный файл базы данных"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            temp_path = f.name
        
        yield temp_path
        
        # Cleanup
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    @pytest.fixture
    async def sqlite_tool(self, temp_db_file):
        """DatabaseTool с SQLite подключением"""
        try:
            return create_sqlite_tool(database=temp_db_file)
        except ImportError:
            pytest.skip("SQLAlchemy не установлен")
    
    async def test_create_tool_without_dependencies(self):
        """Тест создания инструмента без зависимостей"""
        # Должен создаваться даже без зависимостей
        tool = DatabaseTool()
        assert isinstance(tool, DatabaseTool)
        assert len(tool.connections) == 0
    
    async def test_sqlite_connection(self, sqlite_tool):
        """Тест SQLite подключения"""
        assert len(sqlite_tool.connections) == 1
        assert 'default' in sqlite_tool.connections
        
        conn_info = sqlite_tool.connections['default']
        assert conn_info['type'] == 'sql'
        assert 'engine' in conn_info
        assert 'session_maker' in conn_info
    
    async def test_create_table_and_insert(self, sqlite_tool):
        """Тест создания таблицы и вставки данных"""
        # Создаём таблицу
        create_result = await sqlite_tool.execute_sql(
            "CREATE TABLE test_users (id INTEGER PRIMARY KEY, name TEXT, email TEXT)"
        )
        
        assert create_result.success == True
        print(f"✅ Таблица создана: {create_result.message}")
        
        # Вставляем данные
        insert_result = await sqlite_tool.execute_sql(
            "INSERT INTO test_users (name, email) VALUES ('Андрей', 'andrey@cyberkitty.ru')"
        )
        
        assert insert_result.success == True
        assert insert_result.data['affected_rows'] == 1
        print(f"✅ Данные вставлены: {insert_result.message}")
    
    async def test_select_data(self, sqlite_tool):
        """Тест выборки данных"""
        # Создаём и заполняем таблицу
        await sqlite_tool.execute_sql(
            "CREATE TABLE test_products (id INTEGER PRIMARY KEY, name TEXT, price REAL)"
        )
        
        await sqlite_tool.execute_sql(
            "INSERT INTO test_products (name, price) VALUES ('KittyCore License', 99.99)"
        )
        
        # Выбираем данные
        select_result = await sqlite_tool.execute_sql(
            "SELECT * FROM test_products"
        )
        
        assert select_result.success == True
        assert select_result.data['data'] is not None
        assert len(select_result.data['data']) == 1
        
        product = select_result.data['data'][0]
        assert product['name'] == 'KittyCore License'
        assert product['price'] == 99.99
        
        print(f"✅ Данные выбраны: {product}")
    
    async def test_list_tables(self, sqlite_tool):
        """Тест получения списка таблиц"""
        # Создаём несколько таблиц
        await sqlite_tool.execute_sql("CREATE TABLE users (id INTEGER, name TEXT)")
        await sqlite_tool.execute_sql("CREATE TABLE products (id INTEGER, title TEXT)")
        
        # Получаем список таблиц
        tables_result = await sqlite_tool.list_tables()
        
        assert tables_result.success == True
        assert tables_result.data['total_tables'] == 2
        
        table_names = [t['name'] for t in tables_result.data['tables']]
        assert 'users' in table_names
        assert 'products' in table_names
        
        print(f"✅ Найдены таблицы: {table_names}")
    
    async def test_sql_validation(self, sqlite_tool):
        """Тест валидации SQL запросов"""
        # Опасный запрос должен быть заблокирован
        dangerous_result = await sqlite_tool.execute_sql("DROP TABLE users")
        
        assert dangerous_result.success == False
        assert "Небезопасный SQL запрос" in dangerous_result.error
        
        print(f"✅ Опасный запрос заблокирован: {dangerous_result.error}")
    
    async def test_connect_database_action(self, temp_db_file):
        """Тест действия connect_database"""
        tool = DatabaseTool()
        
        try:
            result = await tool.connect_database(
                db_type='sqlite',
                connection_name='test_conn',
                database=temp_db_file
            )
            
            assert result.success == True
            assert result.data['connection_name'] == 'test_conn'
            assert result.data['db_type'] == 'sqlite'
            
            print(f"✅ Подключение создано: {result.message}")
            
        except Exception as e:
            if "SQLAlchemy не установлен" in str(e):
                pytest.skip("SQLAlchemy не установлен")
            else:
                raise
    
    async def test_get_connection_info(self, sqlite_tool):
        """Тест получения информации о подключении"""
        info_result = await sqlite_tool.get_connection_info()
        
        assert info_result.success == True
        assert info_result.data['connection_name'] == 'default'
        assert info_result.data['db_type'] == 'sqlite'
        assert info_result.data['connection_type'] == 'sql'
        
        print(f"✅ Информация о подключении: {info_result.data}")
    
    async def test_nonexistent_connection(self, sqlite_tool):
        """Тест работы с несуществующим подключением"""
        result = await sqlite_tool.execute_sql("SELECT 1", connection_name='nonexistent')
        
        assert result.success == False
        assert "не найдено" in result.error
    
    async def test_execute_action_method(self, sqlite_tool):
        """Тест метода execute_action"""
        # Тест execute_sql через execute_action
        result = await sqlite_tool.execute_action(
            "execute_sql",
            query="SELECT 1 as test_column"
        )
        
        assert result.success == True
        assert result.data['data'][0]['test_column'] == 1
        
        print(f"✅ execute_action работает: {result.data}")
    
    async def test_unknown_action(self, sqlite_tool):
        """Тест неизвестного действия"""
        result = await sqlite_tool.execute_action("unknown_action")
        
        assert result.success == False
        assert "Неизвестное действие" in result.error

class TestFactoryFunctions:
    """Тесты фабричных функций"""
    
    def test_create_database_tool(self):
        """Тест create_database_tool"""
        try:
            tool = create_database_tool('sqlite', database='test.db')
            assert isinstance(tool, DatabaseTool)
            print("✅ create_database_tool работает")
        except ImportError:
            pytest.skip("SQLAlchemy не установлен")
    
    def test_create_sqlite_tool(self):
        """Тест create_sqlite_tool"""
        try:
            tool = create_sqlite_tool('test.db')
            assert isinstance(tool, DatabaseTool)
            print("✅ create_sqlite_tool работает")
        except ImportError:
            pytest.skip("SQLAlchemy не установлен")


if __name__ == "__main__":
    # Запуск тестов напрямую
    async def run_tests():
        """Запуск основных тестов"""
        print("🧪 Запуск тестов DatabaseTool...")
        
        try:
            # Тест 1: Создание инструмента
            tool = DatabaseTool()
            print("✅ DatabaseTool создан")
            
            # Тест 2: Проверка действий
            actions = tool.get_available_actions()
            print(f"✅ Доступно действий: {len(actions)}")
            
            # Тест 3: Тест без зависимостей
            try:
                sqlite_tool = create_sqlite_tool(':memory:')
                print("✅ SQLite инструмент создан")
                
                # Тест 4: Создание таблицы
                result = await sqlite_tool.execute_sql(
                    "CREATE TABLE test (id INTEGER, name TEXT)"
                )
                print(f"✅ CREATE TABLE: {result.success}")
                
                # Тест 5: Вставка данных
                result = await sqlite_tool.execute_sql(
                    "INSERT INTO test (name) VALUES ('KittyCore')"
                )
                print(f"✅ INSERT: {result.success}, строк: {result.data.get('affected_rows', 0)}")
                
                # Тест 6: Выборка данных
                result = await sqlite_tool.execute_sql("SELECT * FROM test")
                print(f"✅ SELECT: {result.success}, записей: {len(result.data.get('data', []))}")
                
            except ImportError as e:
                print(f"⚠️ SQLAlchemy не установлен: {e}")
                
        except Exception as e:
            print(f"❌ Ошибка тестов: {e}")
        
        print("🎉 Базовые тесты завершены!")
    
    # Запуск тестов
    asyncio.run(run_tests())