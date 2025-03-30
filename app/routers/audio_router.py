import os

from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from fastapi.security import (
    HTTPBearer,
    HTTPAuthorizationCredentials,
)

from app.database.database_helper import db_helper
from app.repositories.audio_db_repo import AudioFileDB
from app.repositories.auth_router_repo import AuthRepo
from app.repositories.upload_audio_repo import UARepo
from app.config.app_config import AUDIO_STORAGE_PATH
from app.schemas.schemas import SchAudioFileResponse
from app.config.logger import get_logger

audio_router = APIRouter(
    tags=["🎼 Upload Audio"],
    prefix="/audio",
)

security = HTTPBearer()
logger = get_logger()


@audio_router.post("/upload/")
async def upload_audio(
    file: UploadFile = File(...),
    custom_name: str = Form(...),
    user_info: HTTPAuthorizationCredentials = Depends(security),
    session=Depends(db_helper.get_session),
) -> SchAudioFileResponse:
    # Декодируем токен и проверяем пользователя
    user_info = AuthRepo.check_current_user(user_info.credentials)

    file_extension = file.filename.split(".")[-1].lower()
    yandex_id = user_info["yandex_id"]

    # Проверка на допустимость имени файла и расширения файла
    UARepo.check_valid_name(custom_name)
    UARepo.check_valid_extension(file_extension)
    logger.info(
        f"Проверка имени файла '{custom_name}' и расширения '{file_extension}' прошла успешно"
    )

    path = f"{AUDIO_STORAGE_PATH}/{yandex_id}/"
    # Создание директории пользователя, если она не существует
    if not os.path.exists(path):
        os.makedirs(f"{path}")
        logger.info(
            f"Создана директория для пользователя с yandex_id {yandex_id}: {path}"
        )

    file_location = f"{path}{custom_name}.{file_extension}"
    try:
        # Сохранение файла на диск в директории
        await UARepo.save_audio(file, file_location)
        # Сохранение информации о файле в базе данных
        response = await AudioFileDB.create_audio(
            yandex_id=yandex_id, filename=custom_name, file_path=path, session=session
        )
    except Exception as e:
        logger.error(f"Ошибка при сохранении/загрузке аудиофайла: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to save/upload audio.")

    logger.info(
        f"Аудиофайл '{custom_name}.{file_extension}' успешно сохранен и записан в директорию: {file_location}"
    )
    return response
