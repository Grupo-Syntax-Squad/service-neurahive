from fastapi import APIRouter, Depends
from constants import Role
from database import get_db
from database.models import User
from modules.user import CreateUser
from schemas.user import PostUser
from sqlalchemy.orm import Session
from auth import check_role, CurrentUser, get_current_user

router = APIRouter(prefix="/users")


@router.get("/")
def get_users(current_user: CurrentUser = Depends(get_current_user)):
    check_role(current_user, Role.ADMIN.value)
    return True


@router.post("/")
def post_user(request: PostUser,  current_user: CurrentUser = Depends(get_current_user), session: Session = Depends(get_db)):
    check_role(current_user, Role.ADMIN.value)
    return CreateUser(session, request).execute()
