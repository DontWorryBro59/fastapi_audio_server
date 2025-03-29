from fastapi import APIRouter
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
    access_token = token_data.get("access_token")
    refresh_token = token_data.get("refresh_token")
    print(access_token)
    print(refresh_token)

