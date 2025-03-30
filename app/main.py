import os
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from app.config.app_config import AUDIO_STORAGE_PATH
from app.database.database_helper import db_helper
from app.config.logger import get_logger

# импорт маршрутов
from app.routers.audio_router import audio_router
from app.routers.auth_router import auth_router
from app.routers.users_router import users_router
from app.routers.admin_router import admin_router

logger = get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Убедимся, что директория для сохранения аудио файлов существует
    logger.info("Проверка директории для сохранения аудио файлов")
    if not os.path.exists(AUDIO_STORAGE_PATH):
        try:
            os.makedirs(AUDIO_STORAGE_PATH)
            logger.info("Директория успешно создана")
        except Exception as e:
            logger.error(f"Ошибка при создании директории для аудио: {e}")
            raise Exception(f"Ошибка при создании директории для аудио: {e}")
    await db_helper.create_all()
    logger.info("База данных создана")
    logger.info("Запуск приложения")
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(auth_router)
app.include_router(audio_router)
app.include_router(users_router)
app.include_router(admin_router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
