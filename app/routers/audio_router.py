import os

from fastapi import APIRouter, UploadFile, File, Form, Depends
from fastapi.security import (
    HTTPBearer,
    HTTPAuthorizationCredentials,
)

from app.repositories.auth_router_repo import AuthRepo
from app.repositories.upload_audio_repo import ua_repo
from app.schemas.response_schemas import Sch_Upload_Audio
from config.app_config import AUDIO_STORAGE_PATH

audio_router = APIRouter(
    tags=["🎼 Upload Audio"],
    prefix="/audio",
)

security = HTTPBearer()


@audio_router.post("/upload/")
async def upload_audio(
    file: UploadFile = File(...),
    custom_name: str = Form(...),
    user_info: HTTPAuthorizationCredentials = Depends(security),
) -> Sch_Upload_Audio:
    # Декодируем токен и проверяем пользователя
    user_info = AuthRepo.check_current_user(user_info.credentials)

    file_extension = file.filename.split(".")[-1].lower()

    yandex_id = user_info["yandex_id"]

    # Проверка на допустимость имени файла и расширения файла
    ua_repo.check_valid_name(custom_name)
    ua_repo.check_valid_extension(file_extension)

    path = f"{AUDIO_STORAGE_PATH}/{yandex_id}/"
    # Создание директории пользователя, если она не существует
    if not os.path.exists(path):
        os.makedirs(f"{path}")

    file_location = f"{path}{custom_name}.{file_extension}"

    # Сохранение файла на диск в директории
    await ua_repo.save_audio(file, file_location)

    return {"filename": custom_name, "path": file_location}
