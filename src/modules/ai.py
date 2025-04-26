from datetime import datetime
from fastapi import WebSocketException, status
from sqlalchemy.orm import Session
from src.database.models import ChatHistory
from src.schemas.ai import AiResponse
from src.schemas.chat_payload import ChatPayload


class AiHandler:
    def __init__(self, session: Session, payload: ChatPayload) -> None:
        self._session = session
        self._payload = payload
        self._knowledge_base: str | None = None
        self._ai_response: AiResponse | None = None

    def execute(self) -> AiResponse:
        try:
            with self._session as session:
                self._format_user_message()
                self._add_user_message_to_history(session)
                self._load_knowledge_base()
                self._send_knowledge_base_to_ai()
                self._send_message_to_ai()
                if not self._ai_response:
                    raise WebSocketException(
                        code=status.WS_1011_INTERNAL_ERROR,
                        reason="Erro ao consultar o agente",
                    )
                self._add_ai_response_to_history(session)
                return self._ai_response
        except Exception as e:
            raise WebSocketException(
                code=status.WS_1011_INTERNAL_ERROR,
                reason=f"Erro ao consultar o agente: {e}",
            )

    def _format_user_message(self) -> None:
        self._payload.message = self._payload.message.strip()

    def _add_user_message_to_history(self, session: Session) -> None:
        ChatHistory.add_chat_history(
            session,
            self._payload.chat_id,
            self._payload.message,
            True,
            self._payload.message_date,
        )

    def _load_knowledge_base(self) -> None:
        # TODO: Implement this method
        self._knowledge_base = "knowledge_base"

    def _send_knowledge_base_to_ai(self) -> None:
        # TODO: Implement this method
        pass

    def _send_message_to_ai(self) -> None:
        # TODO: Implement this method
        self._ai_response = AiResponse(
            answer="Not implemented yet!", reponse_date=datetime.now()
        )

    def _add_ai_response_to_history(self, session: Session) -> None:
        if self._ai_response:
            ChatHistory.add_chat_history(
                session,
                self._payload.chat_id,
                self._ai_response.answer,
                False,
                self._ai_response.reponse_date,
            )
