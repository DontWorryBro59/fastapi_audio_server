import re

from fastapi import HTTPException

from app.config.app_config import (
    ALLOWED_AUDIO,
    VALID_FILENAME_PATTERN,
)


class UARepo:

    @classmethod
    def check_valid_name(cls, name) -> None:
        # Проверка на допустимость имени файла
        if not re.match(VALID_FILENAME_PATTERN, name):
            raise HTTPException(
                status_code=400,
                detail="Invalid file name. Only letters, numbers, underscores, dashes, and dots are allowed.",
            )

        if len(name) > 255:
            raise HTTPException(
                status_code=400,
                detail="File name is too long. Maximum length is 255 characters.",
            )

    @classmethod
    def check_valid_extension(cls, file_extension) -> None:
        # Проверка на допустимость расширения файла
        if file_extension not in ALLOWED_AUDIO:
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Only audio files are allowed.",
            )

    @classmethod
    async def save_audio(cls, file, file_location):
        async with aiofiles.open(file_location, "wb") as buffer:
            await buffer.write(await file.read())
        logger.info(f"Файл успешно сохранен по пути: {file_location}")
