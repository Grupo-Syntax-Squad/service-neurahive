from fastapi import Depends, HTTPException, Header, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import List, Optional
from passlib.context import CryptContext
from database.models import User
from database import get_db

SECRET_KEY = "a3b3fa5f2ffb3792b5f98f4431f406a9fbbb933d594ea5d35bc2c84dce3db8b3"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 300000

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

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, user_roles: list[int], expires_delta: timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
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

def get_current_user(token: str = Depends(get_authorization_header), db: Session = Depends(get_db)):    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials"
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        with db as session:
            user = session.query(User).filter(User.id == user_id).first()
            if user is None or not user.enabled:
                raise credentials_exception        
    except JWTError:
        raise credentials_exception
    return CurrentUser.model_validate(user)

def check_role(user: CurrentUser, required_roles: list[int]):
    if not any(role in user.role for role in required_roles):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this resource",
        )