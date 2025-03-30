from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.database.database_helper import db_helper
from app.repositories.auth_router_repo import AuthRepo
from app.repositories.users_db_repo import UserDB
from app.schemas.schemas import (
    SchGetUser,
    SchUpdateUser,
    SchGetAudioFile,
    SchUserChangeResponse,
)
from app.config.logger import get_logger

users_router = APIRouter(tags=["🙍‍♂️ users"], prefix="/users")

security = HTTPBearer()
logger = get_logger()


@users_router.get("/get_user_info/")
async def get_user_info(
    user_info: HTTPAuthorizationCredentials = Depends(security),
    session=Depends(db_helper.get_session),
) -> SchGetUser | None:
    """Получение информации о пользователе"""
    # Декодируем токен и проверяем пользователя
    user_info = AuthRepo.check_current_user(user_info.credentials)
    user_data = await UserDB.get_user_by_yandex_id(user_info["yandex_id"], session)

    if user_data is None:
        logger.error(f"Пользователь с Yandex ID {user_info['yandex_id']} не найден.")
        raise HTTPException(status_code=404, detail="User not found")

    user = SchGetUser.model_validate(user_data)
    logger.info(
        f"Информация о пользователе с Yandex ID {user_info['yandex_id']} успешно получена."
    )
    return user


@users_router.patch("/change_user/")
async def change_user_info(
    update_data: SchUpdateUser,
    user_info: HTTPAuthorizationCredentials = Depends(security),
    session=Depends(db_helper.get_session),
) -> SchUserChangeResponse:
    """Изменение информации о пользователе"""
    logger.info(
        f"Попытка изменить информацию о пользователе с Yandex ID {user_info.credentials}"
    )

    user_info = AuthRepo.check_current_user(user_info.credentials)
    message = await UserDB.change_user(user_info["yandex_id"], update_data, session)

    logger.info(
        f"Информация о пользователе с Yandex ID {user_info['yandex_id']} успешно обновлена."
    )
    return message


@users_router.get("/get_audios_list/")
async def get_audios_list(
    user_info: HTTPAuthorizationCredentials = Depends(security),
    session=Depends(db_helper.get_session),
) -> list[SchGetAudioFile]:
    """Получение списка аудиофайлов пользователя"""
    logger.info(
        f"Получение списка аудиофайлов для пользователя с Yandex ID {user_info.credentials}"
    )

    user_info = AuthRepo.check_current_user(user_info.credentials)
    audios_list = await UserDB.get_audios_list(user_info["yandex_id"], session)

    logger.info(
        f"Список аудиофайлов пользователя с Yandex ID {user_info['yandex_id']} получен."
    )
    return audios_list
