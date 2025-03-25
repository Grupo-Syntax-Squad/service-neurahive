from fastapi import Depends, HTTPException, Header, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Any, List, Optional
from passlib.context import CryptContext
from src.constants import Role
from src.database.models import User
from src.database.get_db import get_db
from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("TOKEN_EXPIRATION_TIME", 30))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Token(BaseModel):
    access_token: str
    token_type: str


class CurrentUser(BaseModel):
    id: int
    email: str
    name: str
    role: List[int]
    enabled: bool

    class Config:
        from_attributes = True


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(
    data: dict[str, Any],
    user_roles: list[int],
    expires_delta: timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
) -> str:
    to_encode = data.copy()
    to_encode["roles"] = user_roles
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_authorization_header(authorization: str = Header(None)) -> Optional[str]:
    if authorization is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header is missing",
        )
    token = authorization.split(" ")[1] if " " in authorization else authorization
    return token


def get_current_user(
    token: str = Depends(get_authorization_header), db: Session = Depends(get_db)
) -> CurrentUser | None:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = int(payload.get("sub", 0))
        if user_id is None:
            raise credentials_exception
        with db as session:
            user = session.query(User).filter(User.id == user_id).first()
            if user is None or not user.enabled:
                raise credentials_exception
    except JWTError:
        raise credentials_exception
    return CurrentUser.model_validate(user)


class PermissionValidator:
    def __init__(
        self,
        user: CurrentUser,
        roles: list[Role] | Role = [Role.ADMIN, Role.CURATOR, Role.CLIENT],
    ):
        self._roles = roles
        self._user = user

    def execute(self) -> None:
        if isinstance(self._roles, list):
            self._verify_roles(self._roles)
        else:
            self._verify_role(self._roles)

    def _verify_role(self, role: Role) -> None:
        if role.value not in self._user.role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this resource",
            )

    def _verify_roles(self, roles: list[Role]) -> None:
        for role in roles:
            self._verify_role(role)
