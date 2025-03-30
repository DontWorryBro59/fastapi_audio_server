from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database_helper import db_helper
from app.repositories.auth_router_repo import AuthRepo
from app.repositories.users_db_repo import UserDB
from app.schemas.schemas import SchUserDeleteResponse
from app.config.logger import get_logger

admin_router = APIRouter(tags=["👨🏻‍💻 admin"], prefix="/admin")

security = HTTPBearer()
logger = get_logger()


# Это необходимо реализовать для суперюзера
@admin_router.delete("/delete_user_by_admin/")
async def delete_user(
    yandex_id: str,
    user_info: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(db_helper.get_session),
) -> SchUserDeleteResponse:
    logger.info(
        f"Пользователь с yandex_id {user_info.credentials} пытается удалить пользователя с yandex_id {yandex_id}"
    )
    user_info = AuthRepo.check_current_user(user_info.credentials)
    user = await UserDB.get_user_by_yandex_id(user_info["yandex_id"], session)

    if user.superuser is False:
        logger.error(
            f"Пользователь с yandex_id {user_info['yandex_id']} не является суперюзером"
        )
        raise HTTPException(status_code=403, detail="Only superuser can do that")

    message = await UserDB.delete_user(yandex_id, session)
    logger.info(
        f"Пользователь с yandex_id {yandex_id} успешно удален администратором с yandex_id {user_info['yandex_id']}"
    )
    return message
