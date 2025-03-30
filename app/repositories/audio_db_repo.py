from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.users import UserORM, AudioFileORM
from app.schemas.schemas import SchAudioFileResponse
from app.config.logger import get_logger

logger = get_logger()

class AudioFileDB:

    @classmethod
    async def create_audio(
        cls, yandex_id: str, filename: str, file_path: str, session: AsyncSession
    ) -> SchAudioFileResponse:
        """Метод для записи данных об аудиофайле в БД"""
        logger.info(f"Попытка создания аудиофайла: {filename} для пользователя с yandex_id: {yandex_id}")
        query = select(UserORM).where(UserORM.yandex_id == yandex_id)
        user = await session.execute(query)
        user = user.scalar_one_or_none()

        if user is None:
            logger.error(f"Пользователь с yandex_id {yandex_id} не найден при создании аудиофайла {filename}")
            raise HTTPException(status_code=404, detail="User not found")

        new_audio = AudioFileORM(
            user_id=user.id, filename=filename, file_path=file_path
        )
        session.add(new_audio)
        try:
            await session.commit()
            logger.info(f"Аудиофайл {filename} успешно создан для пользователя с yandex_id {yandex_id}")
            return SchAudioFileResponse(message="Audio file created successfully")
        except Exception as e:
            await session.rollback()
            logger.error(f"Ошибка при создании аудиофайла {filename} для пользователя с yandex_id {yandex_id}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to create audio file: {str(e)}")
