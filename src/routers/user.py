from fastapi import APIRouter, Depends
from src.auth.auth_utils import PermissionValidator
from src.constants import Role
from src.database.get_db import get_db
from src.modules.user import CreateUser, GetUser, UpdateUser
from src.schemas.basic_response import BasicResponse
from src.schemas.user import GetUserResponse, PostUser, PutUserRequest
from sqlalchemy.orm import Session
from src.auth.auth_utils import CurrentUser, get_current_user

router = APIRouter(prefix="/users")


@router.get("/")
def get_users(
    user_id: int | None = None,
    current_user: CurrentUser = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> BasicResponse[list[GetUserResponse] | GetUserResponse]:
    PermissionValidator(current_user).execute()
    return GetUser(session, user_id).execute()


@router.post("/")
def post_user(
    request: PostUser,
    current_user: CurrentUser = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> BasicResponse[None]:
    PermissionValidator(current_user, Role.ADMIN).execute()
    return CreateUser(session, request).execute()


@router.put("/")
def put_user(
    request: PutUserRequest,
    current_user: CurrentUser = Depends(get_current_user),
    session: Session = Depends(get_current_user),
) -> BasicResponse[None]:
    PermissionValidator(current_user).execute()
    return UpdateUser(session, request).execute()


@router.delete("/")
def delete_user(
    user_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> BasicResponse[None]:
    PermissionValidator(current_user, Role.ADMIN).execute()
    return BasicResponse()
