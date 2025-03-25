import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from database import get_db
from database.models import User
from datetime import timedelta, datetime
from sqlalchemy.orm import Session
from auth import Token, verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES

class LoginForm(BaseModel):
    email: str
    password: str

router = APIRouter(prefix="/auth")

@router.post("/login", response_model=Token)
def login_for_access_token(form_data: LoginForm, db: Session = Depends(get_db)):
    with db as session:
        user = session.query(User).filter(User.email == form_data.email).first()
        if user is None or not verify_password(form_data.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        user.last_login = datetime.utcnow()
        session.commit()
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id)}, user_roles=user.role, expires_delta=access_token_expires
        )       
        return {"access_token": access_token, "token_type": "bearer"}
        
