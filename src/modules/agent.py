import csv
import json
from io import StringIO

from sqlalchemy import select
from src.schemas.basic_response import BasicResponse, GetAgentBasicResponse
from src.database.models import Agent, Group, KnowledgeBase, User
from src.schemas.agent import AgentResponse, PostAgent, GetAgentsRequest
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, UploadFile
from typing import Optional, List


# TODO: MOVE THIS CSV FILE VALIDATOR AND PROCESSING TO ANOTHER CLASS
class CreateAgent:
    def __init__(
        self,
        session: Session,
        name: str,
        theme: str,
        behavior: Optional[str],
        temperature: float,
        top_p: float,
        groups: Optional[List[int]],
        knowledge_base_id: Optional[int],
        file: Optional[UploadFile],
        knowledge_base_name: Optional[str],
    ):
        self.session = session
        self.file = file
        self.knowledge_base_id = knowledge_base_id
        self.name = name
        self.theme = theme
        self.behavior = behavior
        self.temperature = temperature
        self.top_p = top_p
        self.groups = groups
        self.knowledge_base_name = knowledge_base_name

    async def execute(self) -> BasicResponse[AgentResponse]:
        try:
            self._verify_if_knowledge_base_already_have_a_agent()
            agent = await self.create_agent()
            self.session.commit()
            return BasicResponse(data=agent, message="Agente criado com sucesso!")
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                detail=f"Erro ao criar agente: {e}.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _verify_if_knowledge_base_already_have_a_agent(self) -> None:
        if self.knowledge_base_id:
            query = self.session.query(Agent).filter(
                Agent.knowledge_base_id == self.knowledge_base_id
            )
            if query.first():
                raise HTTPException(
                    detail="Base de conhecimento já vinculada a outro agente!",
                    status_code=status.HTTP_409_CONFLICT,
                )

    async def _process_csv_file(self) -> dict[str, list[str]]:
        if self.file and self.file.filename:
            if not self.file.filename.endswith(".csv"):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Apenas arquivos .csv são permitidos.",
                )

        try:
            if self.file:
                contents = await self.file.read()
                try:
                    decoded = contents.decode("utf-8")
                except UnicodeDecodeError:
                    decoded = contents.decode("latin-1")

            csv_reader = csv.DictReader(StringIO(decoded))
            questions, answers = [], []

            for row in csv_reader:
                question = (
                    row.get("pergunta")
                    or row.get("Pergunta")
                    or row.get("perguntas")
                    or row.get("Perguntas")
                )
                answer = (
                    row.get("resposta")
                    or row.get("Resposta")
                    or row.get("respostas")
                    or row.get("Respostas")
                )

                if question and answer:
                    questions.append(question.strip())
                    answers.append(answer.strip())
                    if len(questions) != len(answers):
                        raise ValueError(
                            "Arquivo com quantidade de perguntas diferente da quantidade de respostas"
                        )
                else:
                    raise ValueError(
                        "O arquivo CSV está vazio ou mal formatado. Utilizar arquivo com colunas 'Pergunta' e 'Resposta'"
                    )

            return {"questions": questions, "answers": answers}
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Erro ao processar o arquivo CSV: {e}",
            )

    async def create_agent(self) -> AgentResponse:
        behavior = self.behavior or (
            "Responda de forma clara, útil e educada. Varie o estilo mantendo o sentido original. "
            "Use uma linguagem acessível, mas mantenha profissionalismo."
        )

        if self.file and self.knowledge_base_name:
            knowledge_base_data = await self._process_csv_file()
            new_knowledge_base = KnowledgeBase(
                name=self.knowledge_base_name,
                data=json.dumps(knowledge_base_data),
            )
            self.session.add(new_knowledge_base)
            self.session.flush()
            self.knowledge_base_id = new_knowledge_base.id
        elif self.file and not self.knowledge_base_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A base precisa ter um nome para ser carregada",
            )

        agent = Agent(
            name=self.name,
            behavior=behavior,
            theme=self.theme,
            temperature=self.temperature,
            top_p=self.top_p,
            knowledge_base_id=self.knowledge_base_id,
        )

        if self.groups:
            groups = self.session.query(Group).filter(Group.id.in_(self.groups)).all()
            if len(groups) != len(self.groups):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Um ou mais grupos não foram encontrados.",
                )
            agent.groups = groups

        self.session.add(agent)
        self.session.flush()
        self.session.refresh(agent)

        return AgentResponse(
            id=agent.id,
            name=agent.name,
            theme=agent.theme,
            behavior=agent.behavior,
            temperature=agent.temperature,
            top_p=agent.top_p,
            knowledge_base_id=agent.knowledge_base_id,
            groups=[group.id for group in agent.groups],
        )


class GetAgents:
    def __init__(self, session: Session, params: GetAgentsRequest):
        self._session = session
        self._params = params
        self._user: User | None = None
        self._agents_ids: list[int] | None = None
        self._agents: list[Agent] | None = None
        self._response: list[AgentResponse] | None = None

    def execute(
        self,
    ) -> GetAgentBasicResponse[list[AgentResponse]]:
        try:
            if self._params.user_id:
                self._get_user()
                self._get_user_agents_ids()
            self._get_agents()
            self._make_response()
            return GetAgentBasicResponse(data=self._response)
        except HTTPException as e:
            raise e
        except Exception as e:
            print("[ERROR]:", e)
            raise HTTPException(
                detail=f"Um erro inesperado aconteceu: {e}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _get_user(self) -> None:
        query = select(User).where(User.id == self._params.user_id, User.enabled)
        result = self._session.execute(query)
        self._user = result.unique().scalar_one_or_none()
        if self._user is None:
            raise HTTPException(
                detail="Usuário não encontrado", status_code=status.HTTP_404_NOT_FOUND
            )

    def _get_user_agents_ids(self) -> None:
        if self._user:
            self._agents_ids = [agent.id for agent in self._user.agents]

    def _get_agents(self) -> None:
        query = select(Agent)
        if self._agents_ids:
            query = query.where(Agent.id.in_(self._agents_ids))
        result = self._session.execute(query).unique().scalars().all()
        self._agents = list(result) if result else None

    def _make_response(self) -> None:
        if self._agents:
            self._response = [
                AgentResponse(
                    id=agent.id,
                    name=agent.name,
                    theme=agent.theme,
                    behavior=agent.behavior,
                    temperature=agent.temperature,
                    top_p=agent.top_p,
                    knowledge_base_id=agent.knowledge_base_id,
                    groups=[group.id for group in agent.groups],
                )
                for agent in self._agents
            ]
        else:
            self._response = []


# TODO: Implement this class and call execute method in get individual agent endpoint
class GetAgent: ...


class UpdateAgent:
    def __init__(self, session: Session, agent_id: int, request: PostAgent) -> None:
        self.session = session
        self.agent_id = agent_id
        self.request = request

    def execute(self) -> BasicResponse[AgentResponse]:
        agent = self.update_agent()
        return BasicResponse(data=agent, message="Agent updated successfully.")

    def update_agent(self) -> AgentResponse:
        with self.session as db:
            agent = db.query(Agent).filter(Agent.id == self.agent_id).first()

            if not agent:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Agent not found",
                )

            agent.name = self.request.name

            if self.request.groups is not None:
                groups = db.query(Group).filter(Group.id.in_(self.request.groups)).all()
                if len(groups) != len(self.request.groups):
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="One or more groups not found",
                    )
                agent.groups = groups

            db.commit()
            db.refresh(agent)

            return AgentResponse(
                id=agent.id,
                name=agent.name,
                theme=agent.theme,
                behavior=agent.behavior,
                temperature=agent.temperature,
                top_p=agent.top_p,
                knowledge_base_id=agent.knowledge_base_id,
                groups=[group.id for group in agent.groups],
            )


class DeleteAgent:
    def __init__(self, session: Session, agent_id: int):
        self._session = session
        self._agent_id = agent_id

    def execute(self) -> BasicResponse[None]:
        agent = self._session.query(Agent).filter(Agent.id == self._agent_id).first()
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found"
            )

        self._session.delete(agent)
        self._session.commit()

        return BasicResponse(message="Agent deleted successfully.")
