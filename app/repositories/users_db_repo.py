from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.users import UserORM
from app.schemas.schemas import SchUpdateUser


class UserDB:

    @classmethod
    async def get_user(cls, user_id: int, session: AsyncSession) -> UserORM | None:
        query = select(UserORM).where(UserORM.id == user_id)
        user = await session.execute(query)
        user = user.scalar_one_or_none()
        return user

    @classmethod
    async def get_user_by_yandex_id(cls, yandex_id: int, session: AsyncSession) -> UserORM | None:
        query = select(UserORM).where(UserORM.yandex_id == yandex_id)
        user = await session.execute(query)
        user = user.scalar_one_or_none()
        return user

    @classmethod
    async def create_user(cls, session: AsyncSession, user_data) -> dict:
        new_user = UserORM(**user_data)
        session.add(new_user)
        await session.commit()
        return {"message": "user has been created"}

    @classmethod
    async def change_user(
        cls, yandex_id: int, user_data: SchUpdateUser, session: AsyncSession
    ) -> dict:
        user = await cls.get_user_by_yandex_id(yandex_id, session)

        user_data = user_data.model_dump(exclude_none=True)

        for key, value in user_data.items():
            setattr(user, key, value)

        await session.commit()
        return {"message": f"User with yandex id {yandex_id} has been changed"}
