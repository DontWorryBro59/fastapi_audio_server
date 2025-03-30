import jwt
from fastapi import APIRouter, HTTPException, Depends, status

from app.config.app_config import settings
from app.repositories.auth_router_repo import AuthRepo
from app.repositories.users_db_repo import UserDB
from app.database.database_helper import db_helper
from app.schemas.schemas import SchAuthResponse, SchAuthRedirectResponse
from app.config.logger import get_logger

auth_router = APIRouter(tags=["🔐 auth"], prefix="/auth")
logger = get_logger()


# Формируем URL для перенаправления пользователя
@auth_router.get("/yandex")
async def yandex_auth() -> SchAuthRedirectResponse:
    """Роутер, для получения ссылки/редиректа пользователя к авторизации на Яндексе"""
    redirect_uri = f"https://oauth.yandex.ru/authorize?response_type=code&client_id={settings.YANDEX_CLIENT_ID}"
    logger.info(f"Отправлена ссылка на Яндекс авторизацию: {redirect_uri}")
    return SchAuthRedirectResponse(redirect_url=redirect_uri)


@auth_router.get("/yandex/callback")
async def yandex_callback(
    code: str, session=Depends(db_helper.get_session)
) -> SchAuthResponse:
    """Роутер, для получения токенов пользователя после авторизации на Яндексе"""
    logger.info(f"Получен код авторизации от Яндекса: {code}")

    token_data = await AuthRepo.get_yandex_token(code)

    if token_data.get("error"):
        logger.error(f"Ошибка при получении токенов от Яндекса: {token_data.get('error')}")
        raise HTTPException(status_code=400, detail=token_data.get("error"))

    access_token = token_data.get("access_token")
    if not access_token:
        logger.error("Не удалось получить токен пользователя от Яндекса")
        raise HTTPException(
            status_code=status.HTTP_400, detail="Не удалось получить токен"
        )
    logger.info(f"Получен токен пользователя: {access_token}")

    user_info = await AuthRepo.get_user_info(access_token)

    if not user_info["id"]:
        logger.error("Не удалось получить ID пользователя от Яндекса")
        raise HTTPException(
            status_code=status.HTTP_400, detail="Не удалось получить ID пользователя"
        )

    user_data = {
        "yandex_id": user_info["id"],
        "username": user_info["real_name"],
        "email": user_info["default_email"],
    }

    logger.info(f"Получены данные пользователя: {user_data}")

    new_access_token, new_refresh_token = AuthRepo.create_jwt_tokens(user_data)

    if (
        await UserDB.get_user_by_yandex_id(
            yandex_id=user_data.get("yandex_id"), session=session
        )
        is None
    ):
        await UserDB.create_user(session=session, user_data=user_data)
        logger.info(
            f"Пользователь с Yandex ID {user_data['yandex_id']} добавлен в базу данных."
        )

    return SchAuthResponse(
        yandex_id=user_info["id"],
        access_token=new_access_token,
        refresh_token=new_refresh_token,
    )


@auth_router.post("/refresh")
async def refresh_token(refr_token: str) -> SchAuthResponse:
    """Роутер для обновления токенов пользователя по refresh_token"""
    try:
        logger.info(
            f"Попытка обновления токенов с использованием refresh_token"
        )

        payload = jwt.decode(refr_token, settings.SECRET_KEY, algorithms=["HS256"])
        user_data = {
            "yandex_id": payload.get("yandex_id"),
            "username": payload.get("username"),
            "email": payload.get("email"),
        }
        type_token = payload.get("type")

        if not user_data["yandex_id"] or type_token != "refresh":
            logger.error(f"Некорректный refresh_token: {refr_token}")
            raise HTTPException(status_code=400, detail="Некорректный refresh_token")

        new_access_token, new_refresh_token = AuthRepo.create_jwt_tokens(user_data)

        logger.info(
            f"Созданы новые токены для пользователя с Yandex ID: {user_data['yandex_id']}"
        )

        return SchAuthResponse(
            yandex_id=user_data["yandex_id"],
            access_token=new_access_token,
            refresh_token=new_refresh_token,
        )

    except jwt.ExpiredSignatureError:
        logger.error("Refresh token истек")
        raise HTTPException(status_code=401, detail="Refresh token истек")

    except jwt.InvalidTokenError:
        logger.error("Некорректный refresh_token")
        raise HTTPException(status_code=401, detail="Некорректный refresh_token")
