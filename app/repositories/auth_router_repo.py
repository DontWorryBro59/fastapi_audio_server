from datetime import datetime, timedelta

import aiohttp
import jwt
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer

from app.config.app_config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class AuthRepo:

    @classmethod
    async def get_yandex_token(cls, code):
        url = "https://oauth.yandex.ru/token"
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": settings.YANDEX_CLIENT_ID,
            "client_secret": settings.YANDEX_CLIENT_SECRET,
        }

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, data=data) as response:
                    response.raise_for_status()
                    json_data = await response.json()
                    if not json_data:
                        raise HTTPException(
                            status_code=404, detail="Пустой ответ от Яндекса"
                        )
                    return json_data
            except aiohttp.ClientResponseError as e:
                raise HTTPException(
                    status_code=e.status, detail=f"Ошибка Яндекса: {e.message}"
                )

    @classmethod
    async def get_user_info(cls, access_token):
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    "https://login.yandex.ru/info",
                    headers={"Authorization": f"OAuth {access_token}"},
                ) as response:
                    response.raise_for_status()
                    json_data = await response.json()
                    if not json_data:
                        raise HTTPException(
                            status_code=404, detail="Пустой ответ от Яндекса"
                        )
                    return json_data
            except aiohttp.ClientResponseError as e:
                raise HTTPException(
                    status_code=e.status, detail=f"Ошибка Яндекса: {e.message}"
                )

    @classmethod
    def create_jwt_tokens(cls, user_data: dict) -> tuple[str, str]:
        """Создаёт access_token и refresh_token"""
        access_expiration = datetime.utcnow() + timedelta(
            hours=settings.TOKEN_EXPIRE_HOURS
        )
        refresh_expiration = datetime.utcnow() + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )

        access_payload = {
            **user_data,
            "exp": access_expiration,
            "type": "access",
        }
        refresh_payload = {
            **user_data,
            "exp": refresh_expiration,
            "type": "refresh",
        }

        access_token = jwt.encode(
            access_payload, settings.SECRET_KEY, algorithm="HS256"
        )
        refresh_token = jwt.encode(
            refresh_payload, settings.SECRET_KEY, algorithm="HS256"
        )

        return access_token, refresh_token

    @classmethod
    def check_current_user(cls, access_token: str) -> dict:
        try:
            payload = jwt.decode(
                access_token, settings.SECRET_KEY, algorithms=["HS256"]
            )

            if payload.get("type") != "access":
                raise HTTPException(status_code=401, detail="Invalid token")

            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")
