from fastapi import APIRouter, Depends
from database import get_db
from modules.user import CreateUser
from schemas.user import PostUser
from sqlalchemy.orm import Session

router = APIRouter(prefix="/users")


@router.get("/")
def get_users():
    return True


@router.post("/")
def post_user(request: PostUser, session: Session = Depends(get_db)):
    return CreateUser(session, request).execute()
