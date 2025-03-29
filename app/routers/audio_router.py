import os

from fastapi import APIRouter, UploadFile, File, Form, Depends
from fastapi.security import OAuth2PasswordBearer

from app.repositories.upload_audio_repo import ua_repo
from app.schemas.response_schemas import Sch_Upload_Audio
from app.repositories.auth_router_repo import AuthRepo
from config.app_config import AUDIO_STORAGE_PATH

audio_router = APIRouter(
    tags=["🎼 Upload Audio"],
    prefix="/audio",
)


@audio_router.post("/upload/")
async def upload_audio(
    file: UploadFile = File(...),
    custom_name: str = Form(...),
    user_info: str = Depends(AuthRepo.check_current_user),
) -> Sch_Upload_Audio:

    file_extension = file.filename.split(".")[-1].lower()

    user_id = user_info["user_id"]

    # Проверка на допустимость имени файла и расширения файла
    ua_repo.check_valid_name(custom_name)
    ua_repo.check_valid_extension(file_extension)
    # Создание директории пользователя, если она не существует
    if not os.path.exists(f"{AUDIO_STORAGE_PATH}/{user_id}/"):
        os.makedirs(f"{AUDIO_STORAGE_PATH}/{user_id}/")

    file_location = f"{AUDIO_STORAGE_PATH}/{user_id}/{custom_name}.{file_extension}"

    # Сохранение файла на диск в директории
    await ua_repo.save_audio(file, file_location)

    return {"filename": custom_name, "path": file_location}
