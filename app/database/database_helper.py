from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker, AsyncEngine

from app.config.app_config import settings
from app.models.base_model import Base

# Создаем асинхронный движок
async_engine = create_async_engine(settings.DATABASE_URL)


# Сессия для асинхронных запросов
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine, expire_on_commit=False, class_=AsyncSession
)


class DBHelper:
    def __init__(self, engine: AsyncEngine, async_session: AsyncSession):
        self.async_engine = engine
        self.async_session_maker = async_session

    async def create_all(self) -> None:
        """Создание всех таблиц в базе данных"""
        async with self.async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def drop_all(self) -> None:
        """Удаление всех таблиц из базы данных"""
        async with self.async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Получение асинхронной сессии для работы с базой данных"""
        async with self.async_session_maker() as session:
            yield session


db_helper = DBHelper(async_engine, AsyncSessionLocal)
