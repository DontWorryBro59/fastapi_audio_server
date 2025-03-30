from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.database.database_helper import db_helper
from app.repositories.auth_router_repo import AuthRepo
from app.repositories.users_db_repo import UserDB

admin_router = APIRouter(tags=["👨🏻‍💻 admin"], prefix="/admin")

security = HTTPBearer()


#Это необходимо реализовать для суперюзера
@admin_router.delete("/delete_user_by_admin/")
async def delete_user(
    yandex_id: str,
    user_info: HTTPAuthorizationCredentials = Depends(security),
    session=Depends(db_helper.get_session),
):

    user_info = AuthRepo.check_current_user(user_info.credentials)
    user = await UserDB.get_user_by_yandex_id(user_info["yandex_id"], session)
    if user.superuser is False:
        raise HTTPException(status_code=403, detail="Only superuser can do that")

    message = await UserDB.delete_user(yandex_id, session)
    return message