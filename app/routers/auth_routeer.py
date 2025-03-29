import jwt
from fastapi import APIRouter, HTTPException, Body, Depends
from fastapi.responses import JSONResponse

from app.config.app_config import settings
from app.repositories.auth_router_repo import AuthRepo
from database.database_helper import db_helper
from app.routers.users_db_repo import UserDB

auth_router = APIRouter(tags=["🔐 auth"], prefix="/auth")


# Формируем URL для перенаправления пользователя
@auth_router.get("/yandex")
async def yandex_auth():
    redirect_uri = f"https://oauth.yandex.ru/authorize?response_type=code&client_id={settings.YANDEX_CLIENT_ID}"
    return {"redirect_url": redirect_uri}


@auth_router.get("/yandex/callback")
async def yandex_callback(
    code: str, cid: str = None, session=Depends(db_helper.get_session)
):
    token_data = await AuthRepo.get_yandex_token(code)
    if token_data.get("error"):
        return JSONResponse(content={"error": token_data.get("error")}, status_code=400)

    # Получаем токен пользователя
    access_token = token_data.get("access_token")

    if not access_token:
        return JSONResponse(
            content={"error": "Не удалось получить токены"}, status_code=400
        )
    # Получаем User-ID пользователя с помощью токена
    user_info = await AuthRepo.get_user_info(access_token)

    if not user_info["id"]:
        return JSONResponse(
            content={"error": "Не удалось получить ID пользователя"}, status_code=400
        )

    user_data = {
        "yandex_id": user_info["id"],
        "username": user_info["real_name"],
        "email": user_info["default_email"],
    }
    # Создаём внутренние JWT токены на основе User-ID
    new_access_token, new_refresh_token = AuthRepo.create_jwt_tokens(user_data)

    # Тут будем писать данные в БД
    ###################################################################
    await UserDB.create_user(session=session, user_data=user_data)

    return {
        "yandex_id": user_info["id"],
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
    }


@auth_router.post("/refresh")
async def refresh_token(refr_token: str):
    """Обновляет access_token по refresh_token"""
    try:
        payload = jwt.decode(refr_token, settings.SECRET_KEY, algorithms=["HS256"])
        user_data = {
            "user_id": payload.get("user_id"),
            "username": payload.get("username"),
            "email": payload.get("email"),
        }
        type_token = payload.get("type")
        if not user_data["user_id"] or type_token != "refresh":
            raise HTTPException(status_code=400, detail="Некорректный refresh_token")

        new_access_token, new_refresh_token = AuthRepo.create_jwt_tokens(user_data)
        return {"access_token": new_access_token, "refresh_token": new_refresh_token}

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token истек")

    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Некорректный refresh_token")
