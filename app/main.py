import os
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from app.config.app_config import AUDIO_STORAGE_PATH
from app.database.database_helper import db_helper
from app.routers.audio_router import audio_router
from app.routers.auth_routeer import auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Убедимся, что директория для сохранения аудио файлов существует
    if not os.path.exists(AUDIO_STORAGE_PATH):
        os.makedirs(AUDIO_STORAGE_PATH)
    await db_helper.create_all()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(audio_router)
app.include_router(auth_router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
