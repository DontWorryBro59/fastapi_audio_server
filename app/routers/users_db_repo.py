from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.users import UserORM


class UserDB:

    @classmethod
    async def get_user(cls, user_id: int, session: AsyncSession):
        query = select(UserORM).where(UserORM.id == user_id)
        user = await session.execute(query)
        user = user.scalar_one_or_none()
        if user is None:
            return None
        return user

    @classmethod
    async def get_user_by_yandex_id(cls, yandex_id: int, session: AsyncSession):
        query = select(UserORM).where(UserORM.yandex_id == yandex_id)
        user = await session.execute(query)
        user = user.scalar_one_or_none()
        if user is None:
            return None
        return user

    @classmethod
    async def create_user(cls, session: AsyncSession, user_data):
        new_user = UserORM(**user_data)
        session.add(new_user)
        await session.commit()
