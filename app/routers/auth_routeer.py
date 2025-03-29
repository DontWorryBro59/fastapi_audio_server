import jwt
from fastapi import APIRouter, HTTPException, Body
from fastapi.responses import JSONResponse

from app.config.app_config import settings
from app.repositories.auth_router_repo import AuthRepo

auth_router = APIRouter(tags=["🔐 auth"], prefix="/auth")


# Формируем URL для перенаправления пользователя
@auth_router.get("/yandex")
async def yandex_auth():
    redirect_uri = f"https://oauth.yandex.ru/authorize?response_type=code&client_id={settings.YANDEX_CLIENT_ID}"
    return {"redirect_url": redirect_uri}


@auth_router.get("/yandex/callback")
async def yandex_callback(code: str, cid: str = None):
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
    user_id = user_info.get("id")

    if not user_id:
        return JSONResponse(
            content={"error": "Не удалось получить ID пользователя"}, status_code=400
        )

    # Создаём внутренние JWT токены на основе User-ID
    new_access_token, new_refresh_token = AuthRepo.create_jwt_tokens(user_id)

    return {
        "user_id": user_id,
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
    }


@auth_router.post("/refresh")
async def refresh_token(refr_token: str):
    """Обновляет access_token по refresh_token"""
    print(refr_token)
    try:
        payload = jwt.decode(refr_token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("user_id")
        type_token = payload.get("type")
        if not user_id or type_token != "refresh":
            raise HTTPException(status_code=400, detail="Некорректный refresh_token")

        new_access_token, new_refresh_token = AuthRepo.create_jwt_tokens(user_id)
        return {"access_token": new_access_token, "refresh_token": new_refresh_token}

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token истек")

    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Некорректный refresh_token")
