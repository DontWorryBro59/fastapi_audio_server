import aiohttp
from fastapi import HTTPException

from app.config.app_config import settings


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
                            status_code=500, detail="Пустой ответ от Яндекса"
                        )
                    return json_data
            except aiohttp.ClientResponseError as e:
                raise HTTPException(
                    status_code=e.status, detail=f"Ошибка Яндекса: {e.message}"
                )


