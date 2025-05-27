from enum import Enum
from typing import List
from sqlalchemy import select, update
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
        try:
            with self.session as session:
                self._validate_roles()
                createdUser = self._create_user(session)
                if len(self.request.selected_agents) > 0:
                    self._add_agents_to_user(session, createdUser.id)  # type: ignore[union-attr]
                session.commit()
                return BasicResponse(message="OK")
        except Exception as e:
            raise HTTPException(
                detail=f"Erro ao criar o usuário: {e}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

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

    def _create_user(self, session: Session) -> User | None:
        hashed_password = Auth.get_password_hash(self.request.password)
        user = User(
            name=self.request.name,
            email=self.request.email,
            password=hashed_password,
            role=self.request.role,
            agents=[],
        )
        session.add(user)
        session.flush()
        session.refresh(user)
        return user

    def _add_agents_to_user(self, session: Session, user_id: int) -> GetUserResponse:
        user: User = (
            session.query(User).options(joinedload(User.agents)).get(user_id)  # type: ignore[assignment]
        )
        if not user:
            raise HTTPException(status_code=404, detail="Usuario não encontrado.")
        agents: List[Agent] = (
            session.query(Agent)
            .filter(Agent.id.in_(self.request.selected_agents))
            .all()
        )
        if len(agents) != len(self.request.selected_agents):
            raise HTTPException(
                status_code=404, detail="Alguns agentes não foram encontrados"
            )
        for agent in agents:
            if agent not in user.agents:
                user.agents.append(agent)
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
        self._user: User | None = None
        self._agents: list[Agent] | None = None

    def execute(self) -> BasicResponse[None]:
        try:
            self._hash_new_password()
            self._get_user()
            self._get_selected_agents()
            self._update_user()
            self._session.commit()
            return BasicResponse()
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(
                detail=f"Erro interno: {e}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _hash_new_password(self) -> None:
        self._request.password = Auth.get_password_hash(self._request.password)

    def _get_user(self) -> None:
        query = select(User).where(User.id == self._request.id, User.enabled)
        result = self._session.execute(query)
        self._user = result.unique().scalar_one_or_none()
        if self._user is None:
            raise HTTPException(
                detail="Usuário não encontrado", status_code=status.HTTP_404_NOT_FOUND
            )

    def _get_selected_agents(self) -> None:
        query = select(Agent).where(Agent.id.in_(self._request.selected_agents))
        result = self._session.execute(query)
        agents = result.unique().scalars().all()
        self._agents = list(agents) if agents else []

    def _update_user(self) -> None:
        if self._user:
            self._user.name = self._request.name
            self._user.email = self._request.email
            self._user.password = self._request.password
            self._user.role = self._request.role
            self._user.agents = self._agents
            self._session.add(self._user)


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
