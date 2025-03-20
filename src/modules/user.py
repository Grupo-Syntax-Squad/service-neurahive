from sqlalchemy import text
from auth import get_password_hash
from constants import Role
from schemas.basic_response import BasicResponse
from schemas.user import PostUser
from fastapi import HTTPException, status
from sqlalchemy.orm import Session


class CreateUser:
    def __init__(self, session: Session, request: PostUser):
        self.session = session
        self.request = request

    def execute(self) -> BasicResponse[None]:
        self._validate_roles()
        self._create_user()
        return BasicResponse(message="OK", status_code=status.HTTP_201_CREATED)()

    def _validate_roles(self):
        roles = [Role.ADMIN.value, Role.CURATOR.value, Role.CLIENT.value]
        if len(self.request.role) > len(roles):
            raise HTTPException(
                detail="User have more roles than system has.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        for role in self.request.role:
            if role not in roles:
                raise HTTPException(
                    detail="User have roles that system don't have",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

    def _create_user(self):
        hashed_password = get_password_hash(self.request.password)
        query = text(
            'INSERT INTO "user" (name, email, password, role) VALUES (:name, :email, :password, :role)'
        ).bindparams(
            name=self.request.name,
            email=self.request.email,
            password=hashed_password,
            role=self.request.role,
        )
        with self.session as session:
            session.execute(query)
            session.commit()
