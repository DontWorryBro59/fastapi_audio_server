from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from pydantic import ConfigDict

ALLOWED_AUDIO = {"mp3", "wav", "ogg", "flac", "aac"}
AUDIO_STORAGE_PATH = "audio_storage"
VALID_FILENAME_PATTERN = r"^[a-zA-Z0-9_\-\.]+$"

load_dotenv()

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    YANDEX_CLIENT_ID: str
    YANDEX_CLIENT_SECRET: str
    TOKEN_EXPIRE_HOURS: int
    REFRESH_TOKEN_EXPIRE_DAYS: int

    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()