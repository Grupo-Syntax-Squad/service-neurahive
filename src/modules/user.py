from enum import Enum
from typing import List
from sqlalchemy import update, and_
from src.constants import Role
from src.auth.auth_utils import Auth
from src.database.models import Agent, User
from src.schemas.basic_response import BasicResponse
from src.schemas.user import GetUserResponse, PostUser, PutUserRequest
from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload
from pprint import pprint


class CreateUser:
    def __init__(self, session: Session, request: PostUser):
        self.session = session
        self.request = request

    def execute(self) -> BasicResponse[None]:
        self._validate_roles()
        createdUser = self._create_user()
        if len(self.request.selectedAgents) > 0:
            self._add_agents_to_user(createdUser.id)  # type: ignore[union-attr]
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

    def _create_user(self) -> User | None:
        hashed_password = Auth.get_password_hash(self.request.password)
        with self.session as db:
            user = User(
                name=self.request.name,
                email=self.request.email,
                password=hashed_password,
                role=self.request.role,
                agents=[],
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            return user

    def _add_agents_to_user(self, user_id: int) -> GetUserResponse:
        with self.session as db:
            user: User = (
                db.query(User).options(joinedload(User.agents)).get(user_id)  # type: ignore[assignment]
            )
            if not user:
                raise HTTPException(status_code=404, detail="Usuario não encontrado.")
            agents: List[Agent] = (
                db.query(Agent).filter(Agent.id.in_(self.request.selectedAgents)).all()
            )
            if len(agents) != len(self.request.selectedAgents):
                raise HTTPException(
                    status_code=404, detail="Alguns agentes não foram encontrados"
                )
            for agent in agents:
                if agent not in user.agents:
                    user.agents.append(agent)
            db.commit()
            return GetUserResponse.from_orm(user)


class Operation(Enum):
    ONE_USER = "One user"
    ALL_USERS = "All users"


class GetUser:
    def __init__(self, session: Session, user_id: int | None):
        self._session = session
        self._user_id = user_id
        self.operation: Operation | None = None

    def execute(self) -> BasicResponse[list[GetUserResponse] | GetUserResponse]:
        data: list[GetUserResponse] | GetUserResponse
        try:
            self._define_operation()
            if self.operation == Operation.ALL_USERS:
                data = self._get_users()
            else:
                data = self._get_user()
            pprint(data)
            return BasicResponse(data=data)
        except Exception as e:
            raise HTTPException(
                detail=f"Erro interno: {e}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _define_operation(self) -> None:
        self.operation = Operation.ONE_USER if self._user_id else Operation.ALL_USERS

    def _get_users(self) -> list[GetUserResponse]:
        with self._session as db:
            users = db.query(User).options(joinedload(User.agents)).all()
            serialized_users = [GetUserResponse.from_orm(user) for user in users]
            return serialized_users

    def _get_user(self) -> GetUserResponse:
        with self._session as db:
            user: User = (
                db.query(User).options(joinedload(User.agents)).get(self._user_id)  # type: ignore[assignment]
            )
            if not user:
                raise HTTPException(
                    detail="User doesn't exists", status_code=status.HTTP_404_NOT_FOUND
                )
            serialized_user = GetUserResponse.from_orm(user)
            return serialized_user


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
