from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.database.database_helper import db_helper
from app.repositories.auth_router_repo import AuthRepo
from app.repositories.users_db_repo import UserDB
from app.schemas.schemas import SchGetUser, SchUpdateUser

users_router = APIRouter(tags=["👤 users"], prefix="/users")

security = HTTPBearer()


@users_router.get("/get_user_yaid/")
async def get_user_info(
    user_info: HTTPAuthorizationCredentials = Depends(security),
    session=Depends(db_helper.get_session),
) -> SchGetUser:
    # Декодируем токен и проверяем пользователя
    user_info = AuthRepo.check_current_user(user_info.credentials)
    user_data = await UserDB.get_user_by_yandex_id(user_info["yandex_id"], session)
    user = SchGetUser.model_validate(user_data)
    return user


@users_router.patch("/change_user/")
async def change_user_info(
    update_data: SchUpdateUser,
    user_info: HTTPAuthorizationCredentials = Depends(security),
    session=Depends(db_helper.get_session),
):
    user_info = AuthRepo.check_current_user(user_info.credentials)
    message = await UserDB.change_user(user_info["yandex_id"], update_data, session)
    return message


@users_router.get("/get_audios_list/")
async def get_audios_list(
    user_info: HTTPAuthorizationCredentials = Depends(security),
    session=Depends(db_helper.get_session)):

    user_info = AuthRepo.check_current_user(user_info.credentials)
    audios_list = await UserDB.get_audios_list(user_info["yandex_id"], session)
    return audios_list



#Это необходимо реализовать для суперюзера
@users_router.delete("/delete_user_by_admin/")
async def delete_user(
    user_info: HTTPAuthorizationCredentials = Depends(security),
    session=Depends(db_helper.get_session),
):

    user_info = AuthRepo.check_current_user(user_info.credentials)
    pass
