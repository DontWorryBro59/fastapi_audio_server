from datetime import datetime, timedelta

import aiohttp
import jwt
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer

from app.config.logger import get_logger
from app.config.app_config import settings

logger = get_logger()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class AuthRepo:

    @classmethod
    async def get_yandex_token(cls, code):
        logger.info(f"Получение токена Яндекса для кода: {code}")
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
                        logger.error("Пустой ответ от Яндекса при получении токена")
                        raise HTTPException(
                            status_code=404, detail="Пустой ответ от Яндекса"
                        )
                    logger.info(f"Успешное получение токена Яндекса для кода: {code}")
                    return json_data
            except aiohttp.ClientResponseError as e:
                logger.error(f"Ошибка Яндекса: {e.message} для кода: {code}")
                raise HTTPException(
                    status_code=e.status, detail=f"Ошибка Яндекса: {e.message}"
                )

    @classmethod
    async def get_user_info(cls, access_token):
        logger.info(f"Получение информации о пользователе с токеном")
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    "https://login.yandex.ru/info",
                    headers={"Authorization": f"OAuth {access_token}"},
                ) as response:
                    response.raise_for_status()
                    json_data = await response.json()
                    if not json_data:
                        logger.error("Пустой ответ от Яндекса при получении информации о пользователе")
                        raise HTTPException(
                            status_code=404, detail="Пустой ответ от Яндекса"
                        )
                    logger.info(f"Успешное получение информации о пользователе с токеном")
                    return json_data
            except aiohttp.ClientResponseError as e:
                logger.error(f"Ошибка Яндекса: {e.message} при получении информации о пользователе с токеном")
                raise HTTPException(
                    status_code=e.status, detail=f"Ошибка Яндекса: {e.message}"
                )

    @classmethod
    def create_jwt_tokens(cls, user_data: dict) -> tuple[str, str]:
        """Создаёт access_token и refresh_token"""
        logger.info(f"Создание JWT токенов для пользователя: {user_data.get('username')}")
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
        logger.info(f"Успешное создание JWT токенов для пользователя: {user_data.get('username')}")
        return access_token, refresh_token

    @classmethod
    def check_current_user(cls, access_token: str) -> dict:
        try:
            payload = jwt.decode(
                access_token, settings.SECRET_KEY, algorithms=["HS256"]
            )

            if payload.get("type") != "access":
                logger.error(f"Неверный тип токена: {payload.get('type')} для токена: {access_token}")
                raise HTTPException(status_code=401, detail="Invalid token")
            logger.info(f"Успешная проверка текущего пользователя для токена")
            return payload
        except jwt.ExpiredSignatureError:
            logger.error(f"Токен просрочен: {access_token}")
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.InvalidTokenError:
            logger.error(f"Неверный токен: {access_token}")
            raise HTTPException(status_code=401, detail="Invalid token")
