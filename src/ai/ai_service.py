import requests
from collections import deque
from typing import Any, Deque, Literal, TypedDict
from src.database.models import Agent
from src.settings import Settings
from fastapi import status

settings = Settings()


class Message(TypedDict):
    role: Literal["system", "user", "assistant"]
    content: str


class GeminiComunicationHandler:
    def __init__(
        self, agent: Agent, user_question: str, questions: list[str], answers: list[str]
    ) -> None:
        global settings
        self._agent = agent
        self._user_question = user_question
        self._questions = questions
        self._answers = answers
        self._headers = {
            "Authorization": f"Bearer {settings.AI_API_KEY}",
            "Content-Type": "application/json",
        }
        self._conversation_history: Deque[Message] = deque(maxlen=20)
        self._faq_context: str | None = None
        self._system_message: dict[str, str] | None = None
        self._data: dict[str, Any] | None = None
        self._response: requests.Response | None = None

    def execute(self) -> tuple[str, int]:
        try:
            self._validate_parameters()
            self._format_faq_context()
            self._conversation_history.append(
                {"role": "user", "content": self._user_question}
            )
            self._initialize_system_message()
            self._initialize_data()
            self._make_request_to_gemini()
            self._validate_gemini_response()
            self._conversation_history.append(
                {"role": "assistant", "content": self._gemini_response_message}
            )
            return (self._gemini_response_message, self._gemini_response_created)
        except Exception as e:
            raise Exception(f"Erro ao consultar o Gemini: {e}")

    def _validate_parameters(self) -> None:
        if len(self._questions) != len(self._answers):
            raise ValueError("A quantidade de perguntas e respostas estão divergentes!")

    def _format_faq_context(self) -> None:
        question_and_answers = []
        for c in range(len(self._questions)):
            question = self._questions[c]
            answer = self._answers[c]
            question_and_answers.append(f"Pergunta: {question} | Resposta: {answer}")

        self._faq_context = "\n".join(question_and_answers)

    def _initialize_system_message(self) -> None:
        if not self._agent.behavior:
            self._agent.behavior = (
            "Responda de forma clara, útil e educada. Varie o estilo mantendo o sentido original. "
            "Use uma linguagem acessível, mas mantenha profissionalismo.")

        self._system_message = {
            "role": "system",
            "content": (
                f"Você é um assistente que responde apenas sobre o tema {self._agent.theme}, em pt-br, com base nas perguntas e respostas abaixo."
                f"Se a pergunta não estiver presente ou relacionada ao conteúdo fornecido, diga que só pode responder perguntas sobre o tema {self._agent.theme}, mas se for algo relacionado ao tema pode responder com base no seu conhecimento sobre o tema."
                "diga qual o tema e não fale sobre nada relacionado à pergunta do usuário e nesse caso pode ser uma resposta mais curta."
                f"{self._agent.behavior} \n\n"
                f"{self._faq_context}"
            ),
        }

    def _initialize_data(self) -> None:
        global settings
        messages = [self._system_message] + list(self._conversation_history)
        self._data = {
            "model": settings.AI_MODEL,
            "messages": messages,
            "temperature": self._agent.temperature,  # Variedade nas respostas
            "top_p": self._agent.top_p,  # Garante respostas variadas e criativas
            "n": 1,  # Uma resposta por vez
            "stream": False,  # Resposta completa de uma vez
            "max_tokens": 500,
        }

    def _make_request_to_gemini(self) -> None:
        self._response = requests.post(
            settings.AI_API_URL,  # type: ignore[arg-type]
            json=self._data,
            headers=self._headers,
        )

    def _validate_gemini_response(self) -> None:
        if self._response:
            if self._response.status_code == status.HTTP_200_OK:
                result = self._response.json()
                self._gemini_response_message: str = result["choices"][0]["message"][
                    "content"
                ]
                self._gemini_response_created = result["created"]
            else:
                raise RuntimeError(
                    f"Falha ao buscar dados da API. Código de Status: {self._response.status_code}"
                )
