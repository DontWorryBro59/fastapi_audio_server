import os
import sys
from datetime import datetime, timedelta, UTC

import jwt
import pytest
import pytest_asyncio
from fastapi import HTTPException
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession



# Добавляем корневую папку в путь поиска модулей
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.config.app_config import settings
from app.database.database_helper import DBHelper, db_helper
from app.main import app
from app.models.base_model import Base
from app.repositories.upload_audio_repo import UARepo

# URL тестовой базы данных (SQLite in-memory)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Создаем асинхронный движок и сессию для тестов
test_async_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(
    bind=test_async_engine, expire_on_commit=False, class_=AsyncSession
)

# Создаем тестовый экземпляр DBHelper
test_db_helper = DBHelper(test_async_engine, TestSessionLocal)


@pytest.fixture(scope="session", autouse=True)
def override_db():
    """
    Подменяет зависимость на тестовый DBHelper
    """
    settings.DATABASE_URL = TEST_DATABASE_URL
    app.dependency_overrides[db_helper.get_session] = test_db_helper.get_session
    yield
    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="session")
async def setup_test_db():
    """
    Создает тестовую базу перед тестами и удаляет после
    """
    async with test_async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function", autouse=True)
async def clean_db():
    """
    Очищает базу перед каждым тестом
    """
    await test_db_helper.drop_all()
    await test_db_helper.create_all()
    yield


@pytest_asyncio.fixture(scope="session")
async def async_client():
    """
    Создает асинхронного клиента для тестов
    """
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client


@pytest.fixture
def valid_test_access_token():
    """Создает валидный JWT-токен для тестирования (access token)."""
    payload = {
        "yandex_id": "43141123123",
        "username": "test_user",
        "email": "test@example.com",
        "exp": datetime.now(UTC) + timedelta(hours=settings.TOKEN_EXPIRE_HOURS),
        "type": "access",
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

###################### Пример интеграционных тестов ######################

@pytest.mark.asyncio
async def test_yandex_auth(async_client: AsyncClient):
    """
    Проверяет, что эндпоинт /yandex корректно формирует редирект-ссылку
    Ожидается статус 200 и наличие ключа "redirect_url" в ответе.
    """
    response = await async_client.get("/auth/yandex")

    assert response.status_code == 200
    assert "redirect_url" in response.json()

    expected_url = f"https://oauth.yandex.ru/authorize?response_type=code&client_id={settings.YANDEX_CLIENT_ID}"
    assert response.json()["redirect_url"] == expected_url


@pytest.mark.asyncio
async def test_get_user_info_error(async_client: AsyncClient):
    """
    Проверяет, что эндпоинт /users/get_user_info/ корректно обрабатывает запрос с невалидным токеном.
    Ожидается статус 401 и сообщение "Invalid token".
    """
    headers = {"Authorization": "Bearer test_token"}
    response = await async_client.get("/users/get_user_info/", headers=headers)

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token"


@pytest.mark.asyncio
async def test_get_user_info(async_client: AsyncClient, valid_test_access_token):
    """
    Проверяет, что эндпоинт /users/get_user_info/ с валидным токеном корректно возвращает информацию о пользователе.
    Ожидается статус 404 и сообщение "User not found".
    Тест проверяет работу эндпоинта при отсутствии пользователя с указанным yandex_id в базе данных.
    """
    headers = {"Authorization": f"Bearer {valid_test_access_token}"}
    response = await async_client.get("/users/get_user_info/", headers=headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"

###################### Пример функциональных тестов ######################

@pytest.mark.parametrize(
    "file_name, should_raise_exception, expected_detail",
    [
        ("valid_file_name", False, None),
        ("invalid@file_name", True, "Invalid file name. Only letters, numbers, underscores, dashes, and dots are allowed."),
        ("invalid file name", True, "Invalid file name. Only letters, numbers, underscores, dashes, and dots are allowed."),
        ("a" * 256, True, "File name is too long. Maximum length is 255 characters."),
        ("", True, "Invalid file name. Only letters, numbers, underscores, dashes, and dots are allowed."),
    ]
)
def test_check_valid_name(file_name, should_raise_exception, expected_detail):
    """Тестируем метод check_valid_name с разными входными данными"""
    if should_raise_exception:
        with pytest.raises(HTTPException) as exc:
            UARepo.check_valid_name(file_name)
        assert exc.value.status_code == 400
        assert exc.value.detail == expected_detail
    else:
        try:
            UARepo.check_valid_name(file_name)
        except HTTPException as e:
            pytest.fail(f"Unexpected HTTPException raised: {e.detail}")