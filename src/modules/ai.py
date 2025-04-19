from datetime import datetime
from fastapi import WebSocketException, status

from src.schemas.ai import AiResponse


class AiHandler:
    def __init__(self, user_id: int, message: str) -> None:
        self._user_id = user_id
        self._message = message
        self._knowledge_base: str | None = None
        self._ai_response: AiResponse | None = None

    async def execute(self) -> AiResponse:
        try:
            self._format_user_message()
            self._load_knowledge_base()
            await self._send_knowledge_base_to_ai()
            await self._send_message_to_ai()
            return self._ai_response
        except Exception as e:
            raise WebSocketException(
                code=status.WS_1011_INTERNAL_ERROR,
                reason=f"Erro ao consultar o agente: {e}",
            )

    def _format_user_message(self) -> None:
        self._message = self._message.strip()

    def _load_knowledge_base(self) -> None:
        # TODO: Implement this method
        self._knowledge_base = "knowledge_base"

    async def _send_knowledge_base_to_ai(self) -> None:
        # TODO: Implement this method
        pass

    async def _send_message_to_ai(self) -> None:
        # TODO: Implement this method
        self._ai_response = AiResponse(
            answer="Not implemented yet!", reponse_date=datetime.now()
        )
