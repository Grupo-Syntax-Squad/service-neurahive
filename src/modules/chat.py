from typing import Any
from sqlalchemy import select, text, update
from src.database.models import Agent, Chat, ChatHistory, User
from src.schemas.basic_response import BasicResponse
from src.schemas.chat import (
    GetChatHistoryRequest,
    GetChatHistoryResponse,
    GetChatsRequest,
    GetChatsResponse,
    PostChat,
)
from sqlalchemy.orm import Session
from fastapi import HTTPException, status


class RouterCreateChat:
    def __init__(self, session: Session, params: PostChat) -> None:
        self._session = session
        self._params = params
        self._new_chat: Chat | None
        self._user: User | None = None

    def execute(self) -> BasicResponse[GetChatsResponse]:
        try:
            self._verify_user_exists()
            self._validate_user_can_create_chat()
            self._verify_agent_exists()
            self._create_chat()
            self._session.commit()
            if self._new_chat is None:
                raise HTTPException(
                    detail="Erro ao criar o chat.",
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
            if self._agent is None:
                raise HTTPException(
                    detail="Erro ao buscar o agente.",
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
            return BasicResponse(
                data=GetChatsResponse(
                    id=self._new_chat.id,
                    enabled=self._new_chat.enabled,
                    agent_id=self._new_chat.agent_id,
                    agent_name=self._agent.name,
                    user_id=self._new_chat.user_id,
                ),
            )
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(
                detail=f"Erro ao criar o chat: {e}.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _verify_user_exists(self) -> None:
        query = select(User).where(User.id == self._params.user_id)
        result = self._session.execute(query).unique()
        self._user = result.scalar_one_or_none()
        if self._user is None:
            raise HTTPException(
                detail=f"Usuário com o id {self._params.user_id} não existe!",
                status_code=status.HTTP_404_NOT_FOUND,
            )

    def _validate_user_can_create_chat(self) -> None:
        if self._user is not None:
            if self._params.agent_id not in self._user.agents:
                raise HTTPException(
                    detail="Não é possível criar um chat com um agente não permitido ao usuário",
                    status_code=status.HTTP_412_PRECONDITION_FAILED,
                )

    def _verify_agent_exists(self) -> None:
        query = select(Agent).where(Agent.id == self._params.agent_id)
        result = self._session.execute(query).unique()
        self._agent = result.scalars().first()
        if self._agent is None:
            raise HTTPException(
                detail=f"Agente com o id {self._params.agent_id} não existe!",
                status_code=status.HTTP_404_NOT_FOUND,
            )

    def _create_chat(self) -> None:
        self._initialize_new_chat()
        self._session.add(self._new_chat)
        self._session.flush()
        self._session.refresh(self._new_chat)

    def _initialize_new_chat(self) -> None:
        self._new_chat = Chat(
            user_id=self._params.user_id, agent_id=self._params.agent_id
        )


class RouterGetChats:
    def __init__(self, session: Session, params: GetChatsRequest):
        self._session = session
        self._params = params

    def execute(self) -> BasicResponse[list[GetChatsResponse]]:
        try:
            self._create_query_conditions()
            self._create_query_params()
            self._get_chats()
            return BasicResponse(data=self._chats)
        except Exception as e:
            raise HTTPException(
                detail=f"Erro ao consultar os chats: {e}.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _create_query_conditions(self) -> None:
        self._conditions: list[str] = []
        if self._params.user_id is not None:
            self._conditions.append("c.user_id = :user_id")
        if self._params.enabled is not None:
            self._conditions.append("c.enabled = :enabled")

    def _create_query_params(self) -> None:
        self._query_params: dict[str, Any] = {}
        if self._params.user_id is not None:
            self._query_params["user_id"] = self._params.user_id
        if self._params.enabled is not None:
            self._query_params["enabled"] = self._params.enabled

    def _get_chats(self) -> None:
        with self._session as session:
            query = "SELECT c.id, c.user_id, c.agent_id, c.enabled, a.name as agent_name FROM chat c JOIN agent a ON c.agent_id = a.id WHERE 1=1"
            if self._conditions:
                query += " AND " + " AND ".join(self._conditions)

            result = (
                session.execute(text(query).bindparams(**self._query_params))
                .mappings()
                .all()
            )
        self._chats = [GetChatsResponse(**row) for row in result]


class RouterDeleteChat:
    def __init__(self, session: Session, chat_id: int) -> None:
        self._session = session
        self._chat_id = chat_id

    def execute(self) -> BasicResponse[None]:
        try:
            with self._session as session:
                self._verify_chat_exists(session)
                self._delete_chat(session)
            return BasicResponse(message="Chat deletado com sucesso!")
        except Exception as e:
            raise HTTPException(
                detail=f"Erro ao deletar o chat {self._chat_id}: {e}. Tente novamente.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _verify_chat_exists(self, session: Session) -> None:
        if Chat.get_chat_by_id(session, self._chat_id) is None:
            raise HTTPException(
                detail=f"Chat com o id {self._chat_id} não existe!",
                status_code=status.HTTP_404_NOT_FOUND,
            )

    def _delete_chat(self, session: Session) -> None:
        session.execute(
            update(Chat).values(enabled=False).where(Chat.id == self._chat_id)
        )
        session.commit()


class RouterGetChatHistory:
    def __init__(self, session: Session, params: GetChatHistoryRequest):
        self._session = session
        self._params = params
        self._chat_history: list[ChatHistory]
        self._response: list[GetChatHistoryResponse]

    def execute(self) -> BasicResponse[list[GetChatHistoryResponse]]:
        try:
            with self._session as session:
                self._verify_chat_exists(session)
                self._get_chat_history(session)
                self._format_response()
                return BasicResponse(data=self._response)
        except Exception as e:
            raise HTTPException(
                detail=f"Erro ao buscar o histórico do chat de id {self._params.chat_id}: {e}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _verify_chat_exists(self, session: Session) -> None:
        if Chat.get_chat_by_id(session, self._params.chat_id) is None:
            raise HTTPException(
                detail=f"Chat com o id {self._params.chat_id} não existe!",
                status_code=status.HTTP_404_NOT_FOUND,
            )

    def _get_chat_history(self, session: Session) -> None:
        query = select(ChatHistory).where(ChatHistory.chat_id == self._params.chat_id)
        result = session.execute(query)
        self._chat_history = list(result.scalars().all())

    def _format_response(self) -> None:
        self._response = [
            GetChatHistoryResponse(
                id=chat_history.id,
                chat_id=chat_history.chat_id,
                message=chat_history.message,
                is_user_message=chat_history.is_user_message,
                message_date=chat_history.message_date,
            )
            for chat_history in self._chat_history
        ]
