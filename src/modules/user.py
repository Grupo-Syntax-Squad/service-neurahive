from enum import Enum
from sqlalchemy import text, update, and_
from src.constants import Role
from src.auth.auth_utils import Auth
from src.database.models import User
from src.schemas.basic_response import BasicResponse
from src.schemas.user import GetUserResponse, PostUser, PutUserRequest
from fastapi import HTTPException, status
from sqlalchemy.orm import Session


class CreateUser:
    def __init__(self, session: Session, request: PostUser):
        self.session = session
        self.request = request

    def execute(self) -> BasicResponse[None]:
        self._validate_roles()
        self._create_user()
        return BasicResponse(message="OK", status_code=status.HTTP_201_CREATED)

    def _validate_roles(self) -> None:
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

    def _create_user(self) -> None:
        hashed_password = Auth.get_password_hash(self.request.password)
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


class Operation(Enum):
    ONE_USER = "One user"
    ALL_USERS = "All users"


class GetUser:
    def __init__(self, session: Session, user_id: int | None):
        self._session = session
        self._user_id = user_id
        self.operation: Operation | None = None

    def execute(self) -> BasicResponse[list[GetUserResponse]]:
        data: list[GetUserResponse]
        try:
            self._define_operation()
            if self.operation == Operation.ALL_USERS:
                data = self._get_users()
            else:
                data = self._get_user()
            return BasicResponse(data=data)
        except Exception as e:
            raise HTTPException(
                detail=f"Erro interno: {e}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _define_operation(self) -> None:
        self.operation = Operation.ONE_USER if self._user_id else Operation.ALL_USERS

    def _get_users(self) -> list[GetUserResponse]:
        query = text('SELECT * FROM "user" WHERE enabled=TRUE')
        result = self._session.execute(query)
        users = result.fetchall()
        return [GetUserResponse(**user._asdict()) for user in users]

    def _get_user(self) -> list[GetUserResponse]:
        query = text('SELECT * FROM "user" WHERE enabled=TRUE AND id=:id').bindparams(
            id=self._user_id
        )
        result = self._session.execute(query)
        users = result.fetchall()
        if len(users) < 1:
            raise HTTPException(
                detail="User doesn't exists", status_code=status.HTTP_404_NOT_FOUND
            )
        return [GetUserResponse(**users[0]._asdict())]


class UpdateUser:
    def __init__(self, session: Session, request: PutUserRequest) -> None:
        self._session = session
        self._request = request

    def execute(self) -> BasicResponse[None]:
        try:
            self._update_user()
            self._session.commit()
            return BasicResponse()
        except Exception as e:
            raise HTTPException(
                detail=f"Erro interno: {e}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _update_user(self) -> None:
        hashed_password = Auth.get_password_hash(self._request.password)
        query = (
            update(User)
            .where(and_(User.id == self._request.id, User.enabled == True))  # noqa E712
            .values(
                email=self._request.email,
                password=hashed_password,
                name=self._request.name,
                role=self._request.role,
            )
        )
        self._session.execute(query)


class DeactivateUser:
    def __init__(self, session: Session, user_id: int) -> None:
        self._session = session
        self._user_id = user_id

    def execute(self) -> BasicResponse[None]:
        try:
            self._deactivate_user()
            self._session.commit()
            return BasicResponse()
        except Exception as e:
            raise HTTPException(
                detail=f"Erro interno: {e}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _deactivate_user(self) -> None:
        query = update(User).where(User.id == self._user_id).values(enabled=False)
        self._session.execute(query)
