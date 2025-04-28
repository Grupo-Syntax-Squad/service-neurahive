from datetime import datetime
from fastapi import WebSocketException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from src.ai.ai_service import GeminiComunicationHandler
from src.database.models import Agent, Chat, ChatHistory, KnowledgeBase
from src.schemas.ai import AiResponse
from src.schemas.chat_payload import ChatPayload


class AiHandler:
    def __init__(self, session: Session, payload: ChatPayload) -> None:
        self._session = session
        self._payload = payload
        self._knowledge_base: KnowledgeBase | None = None
        self._agent: Agent | None = None
        self._ai_response: AiResponse | None = None

    def execute(self) -> AiResponse:
        try:
            with self._session as session:
                self._verify_chat_exists(session)
                self._format_user_message()
                self._add_user_message_to_history(session)
                self._load_knowledge_base(session)
                self._get_agent(session)
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

    def _verify_chat_exists(self, session: Session) -> None:
        if not Chat.get_chat_by_id(session, self._payload.chat_id):
            raise WebSocketException(
                reason=f"Chat com o id {self._payload.chat_id} não existe!",
                code=status.WS_1003_UNSUPPORTED_DATA,
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

    def _load_knowledge_base(self, session: Session) -> None:
        query = (
            select(KnowledgeBase)
            .join(Chat, Chat.id == self._payload.chat_id)
            .join(Agent, Agent.id == Chat.agent_id)
            .where(KnowledgeBase.id == Agent.knowledge_base_id)
        )
        result = session.execute(query)
        self._knowledge_base = result.scalars().first()
        if not self._knowledge_base:
            raise WebSocketException(
                reason="Não foi possível encontrar a base de conhecimento do agente!",
                code=status.WS_1013_TRY_AGAIN_LATER,
            )

    def _get_agent(self, session: Session) -> None:
        query = (
            select(Agent)
            .join(Chat, Chat.id == self._payload.chat_id)
            .where(Agent.id == Chat.agent_id)
        )
        result = session.execute(query)
        self._agent = result.scalars().first()
        if not self._agent:
            raise WebSocketException(
                reason="Não foi possível encontrar o agente!",
                code=status.WS_1013_TRY_AGAIN_LATER,
            )

    def _send_message_to_ai(self) -> None:
        if self._agent and self._knowledge_base:
            questions = list(self._knowledge_base.data["questions"])  # type: ignore[index]
            answers = list(self._knowledge_base.data["answers"])  # type: ignore[index]
            ai_answer, response_date = GeminiComunicationHandler(
                self._agent,
                self._payload.message,
                questions,
                answers,
            ).execute()
            self._ai_response = AiResponse(
                answer=ai_answer, response_date=response_date
            )

    def _add_ai_response_to_history(self, session: Session) -> None:
        if self._ai_response:
            ChatHistory.add_chat_history(
                session,
                self._payload.chat_id,
                self._ai_response.answer,
                False,
                datetime.fromtimestamp(self._ai_response.response_date),
            )
