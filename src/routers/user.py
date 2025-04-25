from src.constants import Role
from sqlalchemy.orm import Session
from src.database.get_db import get_db
from fastapi import APIRouter, Depends
from src.auth.auth_utils import PermissionValidator
from src.schemas.auth import CurrentUser
from src.schemas.basic_response import BasicResponse
from src.auth.auth_utils import Auth
from src.schemas.user import GetUserResponse, PostUser, PutUserRequest
from src.modules.user import CreateUser, DeactivateUser, GetUser, UpdateUser

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/")
def get_users(
    current_user: CurrentUser = Depends(Auth.get_current_user),
    session: Session = Depends(get_db),
) -> BasicResponse[list[GetUserResponse] | GetUserResponse]:
    PermissionValidator(current_user, Role.ADMIN).execute()
    return GetUser(session, None).execute()()  # type: ignore[return-value]


@router.get("/{id}")
def get_user(
    id: int,
    current_user: CurrentUser = Depends(Auth.get_current_user),
    session: Session = Depends(get_db),
) -> BasicResponse[list[GetUserResponse] | GetUserResponse]:
    if (current_user.id != id):
        PermissionValidator(current_user, Role.ADMIN).execute()
    return GetUser(session, id).execute()()  # type: ignore[return-value]


@router.post("/")
def post_user(
    request: PostUser,
    current_user: CurrentUser = Depends(Auth.get_current_user),
    session: Session = Depends(get_db),
) -> BasicResponse[None]:
    PermissionValidator(current_user, Role.ADMIN).execute()
    return CreateUser(session, request).execute()()  # type: ignore[return-value]


@router.put("/")
def put_user(
    request: PutUserRequest,
    current_user: CurrentUser = Depends(Auth.get_current_user),
    session: Session = Depends(get_db),
) -> BasicResponse[None]:
    if (current_user.id != request.id):
        PermissionValidator(current_user, Role.ADMIN).execute()
    return UpdateUser(session, request).execute()()  # type: ignore[return-value]


@router.delete("/")
def delete_user(
    user_id: int,
    current_user: CurrentUser = Depends(Auth.get_current_user),
    session: Session = Depends(get_db),
) -> BasicResponse[None]:
    PermissionValidator(current_user, Role.ADMIN).execute()
    return DeactivateUser(session, user_id).execute()()  # type: ignore[return-value]
