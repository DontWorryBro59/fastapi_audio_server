from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class ConfigResponse(BaseModel):
    class Config:
        from_attributes = True


class SchUploadAudio(ConfigResponse):
    filename: str
    path: str


class SchGetUser(ConfigResponse):
    username: str = Field()
    email: EmailStr
    yandex_id: str


class SchUpdateUser(BaseModel):
    username: Optional[str] = Field(default=None, max_length=255, min_length=3)
    email: Optional[EmailStr] = Field(default=None, max_length=255, min_length=3)


class SchGetAudioFile(ConfigResponse):
    filename: str
    file_path: str