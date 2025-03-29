from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.users import UserORM, AudioFileORM


class AudioFileDB:

    @classmethod
    async def create_audio(
        cls, yandex_id: str, filename: str, file_path: str, session: AsyncSession
    ):
        print("creating audio")
        print(yandex_id)
        print(filename)
        print(file_path)
        query = select(UserORM).where(UserORM.yandex_id == yandex_id)
        user = await session.execute(query)
        user = user.scalar_one_or_none()
        print(user)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        new_audio = AudioFileORM(
            user_id=user.id, filename=filename, file_path=file_path
        )
        session.add(new_audio)
        await session.commit()
