from sqlalchemy import text
from src.database.models import Chat
from src.schemas.basic_response import BasicResponse
from src.schemas.chat import GetChatsRequest, GetChatsResponse, PostChat
from sqlalchemy.orm import Session
from fastapi import HTTPException, status


class RouterCreateChat:
    def __init__(self, session: Session, params: PostChat) -> None:
        self._session = session
        self._params = params
        self._new_chat: Chat | None

    def execute(self) -> BasicResponse[None]:
        try:
            with self._session as session:
                self._create_chat(session)
                session.commit()
            return BasicResponse(message="Chat criado com sucesso!")
        except Exception as e:
            raise HTTPException(
                detail=f"Erro ao criar o chat: {e}.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _create_chat(self, session: Session) -> None:
        self._initialize_new_chat()
        session.add(self._new_chat)

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
            self._get_chats()
            return BasicResponse(data=self._chats)
        except Exception as e:
            raise HTTPException(
                detail=f"Erro ao consultar os chats: {e}.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _get_chats(self) -> None:
        with self._session as session:
            params = {}
            conditions: list[str] = []
            if self._params.user_id is not None:
                conditions.append("c.user_id = :user_id")
                params["user_id"] = self._params.user_id
            if self._params.agent_id is not None:
                conditions.append("c.agent_id = :agent_id")
                params["agent_id"] = self._params.agent_id
            if self._params.enabled is not None:
                conditions.append("c.enabled = :enabled")
                params["enabled"] = self._params.enabled

            query = f"""
            SELECT * 
            FROM chat c
            WHERE 1=1
            {f"AND {' AND '.join(conditions)}" if len(conditions) > 0 else ""}
            """
            result = session.execute(text(query).bindparams(**params)).mappings().all()
        self._chats = [GetChatsResponse(**row) for row in result]
