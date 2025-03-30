import re

from fastapi import HTTPException

from app.config.app_config import (
    ALLOWED_AUDIO,
    VALID_FILENAME_PATTERN,
)
from app.config.logger import get_logger

logger = get_logger()


class UARepo:

    @classmethod
    def check_valid_name(cls, name) -> None:
        # Проверка на допустимость имени файла
        if not re.match(VALID_FILENAME_PATTERN, name):
            logger.error(f"Не допустимое имя файла: {name}")
            raise HTTPException(
                status_code=400,
                detail="Invalid file name. Only letters, numbers, underscores, dashes, and dots are allowed.",
            )

        if len(name) > 255:
            logger.error(f"Имя файла слишком длинное: {name}")
            raise HTTPException(
                status_code=400,
                detail="File name is too long. Maximum length is 255 characters.",
            )

    @classmethod
    def check_valid_extension(cls, file_extension) -> None:
        # Проверка на допустимость расширения файла
        if file_extension not in ALLOWED_AUDIO:
            logger.error(f"Не допустимое расширение файла: {file_extension}")
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Only audio files are allowed.",
            )

    @classmethod
    async def save_audio(cls, file, file_location):
        # Сохраняем файл
        with open(file_location, "wb") as buffer:
            buffer.write(await file.read())
            logger.info(f"Файл успешно сохранен по пути: {file_location}")
