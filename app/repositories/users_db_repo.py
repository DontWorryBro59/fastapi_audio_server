from typing import List

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.users import UserORM, AudioFileORM
from app.schemas.schemas import SchUpdateUser, SchGetAudioFile


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

    @classmethod
    async def get_audios_list(cls, yandex_id: int, session: AsyncSession) -> List[SchGetAudioFile]:
        user = await cls.get_user_by_yandex_id(yandex_id, session)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        query = select(AudioFileORM).where(AudioFileORM.user_id == user.id)
        audios_list_orm = await session.execute(query)
        audios_list = audios_list_orm.scalars().all()
        audios_list = [SchGetAudioFile.model_validate(sound) for sound in audios_list]
        return audios_list