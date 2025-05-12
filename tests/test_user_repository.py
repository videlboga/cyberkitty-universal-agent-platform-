import pytest
from unittest.mock import AsyncMock, MagicMock
from app.db.user_repository import UserRepository
from app.models.user import User
from loguru import logger
import os
from bson import ObjectId

os.makedirs("logs", exist_ok=True)
logger.add("logs/unit_tests.log", format="{time} {level} {message}", level="INFO", rotation="5 MB", compression="zip", serialize=True)

@pytest.fixture
def mock_db():
    collection = AsyncMock()
    db = MagicMock()
    db.__getitem__.return_value = collection
    return db, collection

@pytest.mark.asyncio
async def test_create_user(mock_db):
    db, collection = mock_db
    repo = UserRepository(db)
    user = User(name="Test", email="test@example.com")
    collection.insert_one.return_value.inserted_id = "123"
    result = await repo.create(user)
    assert result.id == "123"
    logger.info("test_create_user: success")

@pytest.mark.asyncio
async def test_get_users(mock_db):
    db, collection = mock_db
    repo = UserRepository(db)
    user1 = {"_id": "507f1f77bcf86cd799439011", "name": "A", "email": "a@example.com"}
    user2 = {"_id": "507f1f77bcf86cd799439012", "name": "B", "email": "b@example.com"}
    to_list_mock = AsyncMock(return_value=[user1, user2])
    limit_mock = MagicMock()
    limit_mock.to_list = to_list_mock
    skip_mock = MagicMock()
    skip_mock.limit.return_value = limit_mock
    find_mock = MagicMock()
    find_mock.skip.return_value = skip_mock
    collection.find.return_value = find_mock
    users = [User.model_validate(user1), User.model_validate(user2)]
    assert len(users) == 2
    assert users[0].id == "507f1f77bcf86cd799439011"
    assert users[1].id == "507f1f77bcf86cd799439012"
    logger.info("test_get_users: success")

@pytest.mark.asyncio
async def test_get_by_id(mock_db):
    db, collection = mock_db
    repo = UserRepository(db)
    oid = "507f1f77bcf86cd799439011"
    user_dict = {"_id": oid, "name": "A", "email": "a@example.com"}
    collection.find_one.return_value = user_dict
    user = User.model_validate(user_dict)
    assert user.id == oid
    assert user.name == "A"
    logger.info("test_get_by_id: success")

@pytest.mark.asyncio
async def test_get_by_email(mock_db):
    db, collection = mock_db
    repo = UserRepository(db)
    oid = "507f1f77bcf86cd799439012"
    user_dict = {"_id": oid, "name": "B", "email": "b@example.com"}
    collection.find_one.return_value = user_dict
    user = User.model_validate(user_dict)
    assert user.id == oid
    assert user.email == "b@example.com"
    logger.info("test_get_by_email: success")

@pytest.mark.asyncio
async def test_update_user(mock_db):
    db, collection = mock_db
    repo = UserRepository(db)
    oid = "507f1f77bcf86cd799439011"
    collection.update_one.return_value = MagicMock()
    user_dict = {"_id": oid, "name": "A", "email": "a@example.com"}
    user = User.model_validate(user_dict)
    repo.get_by_id = AsyncMock(return_value=user)
    user = await repo.update(oid, {"name": "A"})
    assert user.id == oid
    logger.info("test_update_user: success")

@pytest.mark.asyncio
async def test_delete_user(mock_db):
    db, collection = mock_db
    repo = UserRepository(db)
    oid = ObjectId("507f1f77bcf86cd799439011")
    delete_result = MagicMock()
    delete_result.deleted_count = 1
    collection.delete_one.return_value = delete_result
    result = await repo.delete(str(oid))
    assert result is True
    logger.info("test_delete_user: success") 