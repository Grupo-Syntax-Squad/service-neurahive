from src.database.models import Chat
from src.schemas.basic_response import BasicResponse
from src.schemas.chat import PostChat
from sqlalchemy.orm import Session
from fastapi import HTTPException, status


class CreateChat:
    def __init__(self, session: Session, params: PostChat) -> None:
        self._session = session
        self._params = params
        self._new_chat: Chat | None

    async def execute(self) -> BasicResponse[None]:
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
