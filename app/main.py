import os
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from app.config.app_config import AUDIO_STORAGE_PATH
from app.routers.audio_router import audio_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Убедимся, что директория для сохранения аудио файлов существует
    if not os.path.exists(AUDIO_STORAGE_PATH):
        os.makedirs(AUDIO_STORAGE_PATH)
    # тут мы будем инициализировать базу данных
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(audio_router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000)
