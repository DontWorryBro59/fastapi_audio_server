import os
import shutil
from typing import List

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.users import UserORM, AudioFileORM
from app.schemas.schemas import (
    SchUpdateUser,
    SchGetAudioFile,
    SchUserDeleteResponse,
    SchUserChangeResponse,
)
from app.config.logger import get_logger

logger = get_logger()


class UserDB:

    @classmethod
    async def get_user(cls, user_id: int, session: AsyncSession) -> UserORM | None:
        """Метод для получения пользователя по id"""
        logger.info(f"Получение пользователя по id: {user_id}")
        query = select(UserORM).where(UserORM.id == user_id)
        user = await session.execute(query)
        user = user.scalar_one_or_none()
        return user

    @classmethod
    async def get_user_by_yandex_id(
        cls, yandex_id: int, session: AsyncSession
    ) -> UserORM | None:
        """Метод для получения пользователя по yandex_id"""
        logger.info(f"Получение пользователя по yandex_id: {yandex_id}")
        query = select(UserORM).where(UserORM.yandex_id == yandex_id)
        user = await session.execute(query)
        user = user.scalar_one_or_none()
        return user

    @classmethod
    async def create_user(cls, session: AsyncSession, user_data) -> dict:
        """Метод для создания пользователя"""
        logger.info(f"Создание пользователя с данными: {user_data}")
        new_user = UserORM(**user_data)
        session.add(new_user)
        await session.commit()
        logger.info(f"Пользователь с yandex_id: {user_data['yandex_id']} успешно создан")
        return {"message": "user has been created"}

    @classmethod
    async def change_user(
        cls, yandex_id: int, user_data: SchUpdateUser, session: AsyncSession
    ) -> SchUserChangeResponse:
        """Метод для изменения пользователя по yandex_id"""
        logger.info(f"Изменение пользователя с yandex_id: {yandex_id}")
        user = await cls.get_user_by_yandex_id(yandex_id, session)
        if user is None:
            logger.error(f"Пользователь с yandex_id: {yandex_id} не найден")
            raise HTTPException(status_code=404, detail="User not found")

        user_data_dict = user_data.model_dump(
            exclude_none=True
        )

        for key, value in user_data_dict.items():
            setattr(user, key, value)

        await session.commit()
        logger.info(f"Пользователь с yandex_id: {yandex_id} успешно изменен")
        return SchUserChangeResponse(
            message=f"User with yandex id {yandex_id} has been changed"
        )

    @classmethod
    async def get_audios_list(
        cls, yandex_id: int, session: AsyncSession
    ) -> List[SchGetAudioFile]:
        """Метод для получения списка аудиозаписей пользователя по yandex_id"""
        logger.info(f"Получение списка аудиозаписей пользователя с yandex_id")
        user = await cls.get_user_by_yandex_id(yandex_id, session)
        if user is None:
            logger.error(f"Пользователь с yandex_id: {yandex_id} не найден")
            raise HTTPException(status_code=404, detail="User not found")

        query = select(AudioFileORM).where(AudioFileORM.user_id == user.id)
        audios_list_orm = await session.execute(query)
        audios_list = audios_list_orm.scalars().all()
        audios_list = [SchGetAudioFile.model_validate(sound) for sound in audios_list]
        logger.info(f"Список аудиозаписей пользователя с yandex_id: {yandex_id} получен")
        return audios_list

    @classmethod
    async def delete_user(
        cls, yandex_id: int, session: AsyncSession
    ) -> SchUserDeleteResponse:
        """Метод для удаления пользователя и всех его аудиозаписей из базы данных и папки в audio_storage"""
        logger.info(f"Удаление пользователя с yandex_id: {yandex_id}")
        user = await cls.get_user_by_yandex_id(yandex_id, session)
        if user is None:
            logger.error(f"Пользователь с yandex_id: {yandex_id} не найден")
            raise HTTPException(status_code=404, detail="User not found")

        # удаляем все аудиозаписи пользователя, прежде чем удалить самого пользователя
        query = select(AudioFileORM).where(AudioFileORM.user_id == user.id)
        audios_list = await session.execute(query)
        audios_list = audios_list.scalars().all()
        for audio in audios_list:
            await session.delete(audio)
        logger.info(f"Удалены все аудиозаписи пользователя с yandex_id: {yandex_id}")
        await session.delete(user)
        await session.commit()
        logger.info(f"Пользователь с yandex_id: {yandex_id} успешно удален")
        # удаляем все аудиозаписи пользователя из audio_storage
        user_folder = os.path.join("audio_storage", user.yandex_id)
        if os.path.exists(user_folder):
            shutil.rmtree(user_folder)  # Удаляет папку со всем содержимым
            logger.info(f"Папка с аудиозаписями пользователя с yandex_id: {yandex_id} успешно удалена")
        return SchUserDeleteResponse(
            message=f"user with yandex id {yandex_id} has been deleted"
        )
