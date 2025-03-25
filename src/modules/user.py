from enum import Enum
from typing import Any, Callable, Union
from sqlalchemy import select, text, update
from src.constants import Role
from src.auth.auth_utils import get_password_hash
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


class Operation(Enum):
    ONE_USER = "One user"
    ALL_USERS = "All users"


class GetUser:
    def __init__(self, session: Session, user_id: int | None):
        self._session = session
        self._user_id = user_id
        self.operation: Operation | None = None
        self.operations: dict[
            Operation, Callable[[], Union[GetUserResponse, list[GetUserResponse]]]
        ] = {
            Operation.ONE_USER: self._get_user,
            Operation.ALL_USERS: self._get_users,
        }

    def execute(self) -> BasicResponse[Union[list[GetUserResponse], GetUserResponse]]:
        self._define_operation()
        data = None
        if self.operation:
            data = self.operations[self.operation]()
        return BasicResponse(data=data, status_code=status.HTTP_302_FOUND)

    def _define_operation(self) -> None:
        self.operation = Operation.ONE_USER if self._user_id else Operation.ALL_USERS

    def _get_users(self) -> list[GetUserResponse]:
        query = select(User)
        result = self._session.execute(query)
        return [GetUserResponse(**user._asdict()) for user in result.fetchall()]

    def _get_user(self) -> GetUserResponse:
        query = select(User).where(User.id == self._user_id)
        result = self._session.execute(query)
        users = result.fetchall()
        if len(users) < 1:
            raise HTTPException(
                detail="User doesn't exists", status_code=status.HTTP_404_NOT_FOUND
            )
        return GetUserResponse(**users[0]._asdict())


class UpdateUser:
    def __init__(self, session: Session, user_data: PutUserRequest) -> None:
        self._session = session
        self._user_data = user_data

    def execute(self) -> BasicResponse[None]:
        self._update_user()
        return BasicResponse()

    def _update_user(self) -> None:
        query = (
            update(User)
            .where(User.id == self._user_data.id)
            .values(
                email=self._user_data.email,
                password=self._user_data.password,
                name=self._user_data.name,
                role=self._user_data.role,
            )
        )
        self._session.execute(query)


class DeleteUser:
    def __init__(self) -> None:
        pass
