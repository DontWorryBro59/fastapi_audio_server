from typing import Optional
from pydantic import BaseModel, EmailStr, Field, constr


class ConfigResponse(BaseModel):
    class Config:
        from_attributes = True
        json_schema_extra = {}


class SchUploadAudio(ConfigResponse):
    filename: str
    path: str


class SchGetUser(ConfigResponse):
    username: str = Field()
    email: EmailStr
    yandex_id: str


class SchUpdateUser(ConfigResponse):
    username: Optional[str] = Field(default=None, max_length=255, min_length=3)
    email: Optional[EmailStr] = Field(default=None, max_length=255, min_length=3)


class SchGetAudioFile(ConfigResponse):
    filename: str
    file_path: str


class SchAudioFileResponse(ConfigResponse):
    message: str

    class Config(ConfigResponse.Config):
        json_schema_extra = {"example": {"message": "Audio file created successfully"}}


class SchUserDeleteResponse(ConfigResponse):
    message: str

    class Config(ConfigResponse.Config):
        json_schema_extra = {
            "example": {"message": "User with yandex_id {yandex_id} has been deleted"}
        }


class SchUserChangeResponse(ConfigResponse):
    message: str

    class Config(ConfigResponse.Config):
        json_schema_extra = {
            "example": {"message": "User with yandex id {yandex_id} has been changed"}
        }


class SchAuthResponse(ConfigResponse):
    yandex_id: str
    access_token: str
    refresh_token: str

    class Config(ConfigResponse.Config):
        json_schema_extra = {
            "example": {
                "yandex_id": "123456",
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            }
        }


class SchAuthRedirectResponse(ConfigResponse):
    redirect_url: str

    class Config(ConfigResponse.Config):
        json_schema_extra = {
            "example": {
                "redirect_url": "https://oauth.yandex.ru/authorize?response_type=code&client_id=123456"
            }
        }
