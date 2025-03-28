from fastapi import APIRouter, UploadFile, File, Form

from app.repositories.upload_audio_repo import ua_repo
from app.schemas.response_schemas import Sch_Upload_Audio

audio_router = APIRouter(
    tags=["🎼 Upload Audio"],
    prefix="/audio",
)


@audio_router.post("/upload/")
async def upload_audio(
    file: UploadFile = File(...),
    custom_name: str = Form(...),
) -> Sch_Upload_Audio:
    file_extension = file.filename.split(".")[-1].lower()

    # Проверка на допустимость имени файла и расширения файла
    ua_repo.check_valid_name(custom_name)
    ua_repo.check_valid_extension(file_extension)

    file_location = f"audio_storage/{custom_name}.{file_extension}"

    # Сохранение файла на диск в директории
    await ua_repo.save_audio(file, file_location)

    return {"filename": custom_name, "path": file_location}
