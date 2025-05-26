from sqlalchemy import select
from src.modules.knowledge_base_handler import KnowledgeBaseHandler
from src.schemas.basic_response import BasicResponse, GetAgentBasicResponse
from src.database.models import Agent, Group, KnowledgeBase, User
from src.schemas.agent import (
    AgentResponse,
    GetAgentRequest,
    GetAgentsRequest,
)
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, UploadFile


class CreateAgent:
    def __init__(
        self,
        session: Session,
        name: str,
        theme: str,
        behavior: str | None,
        temperature: float,
        top_p: float,
        image_id: int,
        groups: list[int] | None,
        knowledge_base_id: int | None,
        file: UploadFile | None,
        knowledge_base_name: str | None,
        enabled: bool,
    ):
        self._session = session
        self._file = file
        self._knowledge_base_id = knowledge_base_id
        self._name = name
        self._theme = theme
        self._behavior = behavior
        self._temperature = temperature
        self._top_p = top_p
        self._image_id = image_id
        self._groups = groups or []
        self._knowledge_base_name = knowledge_base_name
        self._knowledge_base: KnowledgeBase | None = None
        self._enabled = enabled
        self._questions_and_answers: dict[str, list[str]] | None = None
        self._agent: Agent | None = None
        self._response: AgentResponse | None = None

    async def execute(self) -> BasicResponse[AgentResponse]:
        try:
            self._validate()
            await self._handle_knowledge_base()
            await self.create_agent()
            self._make_response()
            self._session.commit()
            return BasicResponse(data=self._agent, message="Agente criado com sucesso")
        except HTTPException as e:
            self._session.rollback()
            raise e
        except Exception as e:
            print("[ERROR]:", e)
            self._session.rollback()
            raise HTTPException(
                detail="Erro ao criar agente",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _validate(self) -> None:
        if self._file and self._knowledge_base_id:
            raise HTTPException(
                detail="Não é possível carregar uma base de conhecimento e selecionar uma existente",
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
            )
        if self._file and not self._knowledge_base_name:
            raise HTTPException(
                detail="A base precisa ter um nome para ser carregada",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        if self._groups:
            self._validate_groups()

    def _validate_groups(self) -> None:
        groups = self._session.query(Group).filter(Group.id.in_(self._groups)).all()
        if len(groups) != len(self._groups):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Um ou mais grupos não foram encontrados.",
            )

    async def _handle_knowledge_base(self) -> None:
        if self._knowledge_base_id:
            self._get_knowledge_base()
            self._verify_if_knowledge_base_already_have_an_agent()
            return
        if self._file:
            await self._process_csv_file()
            self._create_knowledge_base()

    def _get_knowledge_base(self) -> None:
        if self._knowledge_base_id:
            query = select(KnowledgeBase).where(
                KnowledgeBase.id == self._knowledge_base_id
            )
            result = self._session.execute(query)
            self._knowledge_base = result.unique().scalar_one_or_none()
            if self._knowledge_base is None:
                raise HTTPException(
                    detail="Base de conhecimento não encontrada",
                    status_code=status.HTTP_404_NOT_FOUND,
                )

    def _verify_if_knowledge_base_already_have_an_agent(self) -> None:
        if self._knowledge_base_id:
            query = select(Agent).where(
                Agent.knowledge_base_id == self._knowledge_base_id
            )
            result = self._session.execute(query)
            agents = result.unique().scalars().all()
            if len(agents) > 0:
                raise HTTPException(
                    detail="Base de conhecimento já vinculada a outro agente",
                    status_code=status.HTTP_409_CONFLICT,
                )

    async def _process_csv_file(self) -> None:
        if self._file:
            try:
                self._questions_and_answers = await KnowledgeBaseHandler(
                    self._file
                ).execute()
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Erro ao processar o arquivo CSV: {e}",
                )

    def _create_knowledge_base(self) -> None:
        knowledge_base = dict(
            name=self._knowledge_base_name, data=self._questions_and_answers
        )
        self._knowledge_base = KnowledgeBase(**knowledge_base)
        try:
            self._session.add(self._knowledge_base)
            self._session.flush()
            self._session.refresh(self._knowledge_base)
        except Exception as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Erro ao processar o arquivo CSV: {e}",
            )

    async def create_agent(self) -> None:
        if self._knowledge_base:
            self._agent = Agent(
                name=self._name,
                behavior=self._behavior,
                theme=self._theme,
                temperature=self._temperature,
                top_p=self._top_p,
                image_id=self._image_id,
                knowledge_base_id=self._knowledge_base.id,
                groups=self._groups,
                enabled=self._enabled,
            )
        else:
            self._agent = Agent(
                name=self._name,
                behavior=self._behavior,
                theme=self._theme,
                temperature=self._temperature,
                top_p=self._top_p,
                image_id=self._image_id,
                groups=self._groups,
            )
        self._session.add(self._agent)
        self._session.flush()
        self._session.refresh(self._agent)

    def _make_response(self) -> None:
        if self._agent:
            self._response = AgentResponse(
                id=self._agent.id,
                name=self._agent.name,
                theme=self._agent.theme,
                behavior=self._agent.behavior,
                temperature=self._agent.temperature,
                top_p=self._agent.top_p,
                image_id=self._agent.image_id,
                knowledge_base_id=self._agent.knowledge_base_id,
                groups=[group.id for group in self._agent.groups],
                enabled=self._agent.enabled,
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
            # TODO: IMPROVE LOGGING SYSTEM
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
        query = select(Agent).where(Agent.enabled)
        if self._agents_ids is not None:
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
                    image_id=agent.image_id,
                    knowledge_base_id=agent.knowledge_base_id,
                    enabled=agent.enabled,
                    groups=[group.id for group in agent.groups],
                )
                for agent in self._agents
            ]
        else:
            self._response = []


class GetAgent:
    def __init__(self, session: Session, params: GetAgentRequest) -> None:
        self._session = session
        self._params = params
        self._agent: Agent | None = None

    def execute(self) -> GetAgentBasicResponse[AgentResponse]:
        try:
            self._get_agent()
            self._make_response()
            return GetAgentBasicResponse(data=self._response)
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(
                detail=f"Ocorreu um erro inesperado: {e}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _get_agent(self) -> None:
        query = select(Agent).where(Agent.id == self._params.agent_id)
        result = self._session.execute(query)
        self._agent = result.unique().scalar_one_or_none()
        if self._agent is None:
            raise HTTPException(
                detail="Agente não encontrado", status_code=status.HTTP_404_NOT_FOUND
            )

    def _make_response(self) -> None:
        if self._agent:
            self._response = AgentResponse(
                id=self._agent.id,
                name=self._agent.name,
                theme=self._agent.theme,
                behavior=self._agent.behavior,
                temperature=self._agent.temperature,
                top_p=self._agent.top_p,
                image_id=self._agent.image_id,
                knowledge_base_id=self._agent.knowledge_base_id,
                enabled=self._agent.enabled,
                groups=[group.id for group in self._agent.groups],
            )


class UpdateAgent:
    def __init__(
        self,
        session: Session,
        agent_id: int,
        name: str,
        theme: str,
        behavior: str | None,
        temperature: float,
        top_p: float,
        image_id: int,
        groups: list[int] | None,
        knowledge_base_id: int | None,
        enabled: bool,
        file: UploadFile | None,
        knowledge_base_name: str | None,
    ) -> None:
        self._session = session
        self._agent_id = agent_id
        self._file = file
        self._knowledge_base_id = knowledge_base_id
        self._name = name
        self._theme = theme
        self._behavior = behavior
        self._temperature = temperature
        self._top_p = top_p
        self._image_id = image_id
        self._groups = groups or []
        self._knowledge_base_name = knowledge_base_name
        self._enabled = enabled
        self._knowledge_base: KnowledgeBase | None = None
        self._questions_and_answers: dict[str, list[str]] | None = None
        self._agent: Agent | None = None
        self._response: AgentResponse | None = None

    async def execute(self) -> BasicResponse[AgentResponse]:
        self._validate()
        agent = await self.update_agent()
        return BasicResponse(data=agent, message="Agente atualizado com sucesso.")

    def _validate(self) -> None:
        if self._file and self._knowledge_base_id:
            raise HTTPException(
                detail="Não é possível carregar uma base de conhecimento e selecionar uma existente",
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
            )
        if self._file and not self._knowledge_base_name:
            raise HTTPException(
                detail="A base precisa ter um nome para ser carregada",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        if self._groups:
            self._validate_groups()

    def _validate_groups(self) -> None:
        groups = self._session.query(Group).filter(Group.id.in_(self._groups)).all()
        if len(groups) != len(self._groups):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Um ou mais grupos não foram encontrados.",
            )

    async def _handle_knowledge_base(self) -> None:
        if self._knowledge_base_id:
            self._get_knowledge_base()
            self._verify_if_knowledge_base_already_have_an_agent()
            return
        if self._file:
            await self._process_csv_file()
            self._create_knowledge_base()

    def _get_knowledge_base(self) -> None:
        if self._knowledge_base_id:
            query = select(KnowledgeBase).where(
                KnowledgeBase.id == self._knowledge_base_id
            )
            result = self._session.execute(query)
            self._knowledge_base = result.scalar_one_or_none()
            if self._knowledge_base is None:
                raise HTTPException(
                    detail="Base de conhecimento não encontrada",
                    status_code=status.HTTP_404_NOT_FOUND,
                )

    def _verify_if_knowledge_base_already_have_an_agent(self) -> None:
        if self._knowledge_base_id:
            query = select(Agent).where(
                Agent.knowledge_base_id == self._knowledge_base_id
            )
            result = self._session.execute(query)
            agents = result.scalars().all()
            if len(agents) > 0:
                raise HTTPException(
                    detail="Base de conhecimento já vinculada a outro agente",
                    status_code=status.HTTP_409_CONFLICT,
                )

    async def _process_csv_file(self) -> None:
        if self._file:
            try:
                self._questions_and_answers = await KnowledgeBaseHandler(
                    self._file
                ).execute()
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Erro ao processar o arquivo CSV: {e}",
                )

    def _create_knowledge_base(self) -> None:
        knowledge_base = dict(
            name=self._knowledge_base_name, data=self._questions_and_answers
        )
        self._knowledge_base = KnowledgeBase(**knowledge_base)
        self._session.add(self._knowledge_base)
        self._session.flush()
        self._session.refresh(self._knowledge_base)
        self._knowledge_base_id = self._knowledge_base.id

    async def update_agent(self) -> AgentResponse:
        with self._session as db:
            agent = db.query(Agent).filter(Agent.id == self._agent_id).first()

            if not agent:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Agent not found",
                )

            agent.name = self._name
            agent.theme = self._theme
            agent.behavior = self._behavior
            agent.temperature = self._temperature
            agent.enabled = self._enabled
            agent.top_p = self._top_p
            agent.image_id = self._image_id

            if not (self._knowledge_base_id or self._file):
                agent.knowledge_base_id = None
            elif (
                agent.knowledge_base_id
                and agent.knowledge_base_id != self._knowledge_base_id
            ) or self._file:
                await self._handle_knowledge_base()

            if self._knowledge_base_id:
                agent.knowledge_base_id = self._knowledge_base_id

            if self._groups is not None:
                groups = db.query(Group).filter(Group.id.in_(self._groups)).all()
                if len(groups) != len(self._groups):
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
                image_id=agent.image_id,
                knowledge_base_id=agent.knowledge_base_id,
                enabled=agent.enabled,
                groups=[group.id for group in agent.groups],
            )


class DeleteAgent:
    def __init__(self, session: Session, agent_id: int):
        self._session = session
        self._agent_id = agent_id

    def execute(self) -> BasicResponse[None]:
        try:
            self._get_agent()
            self._delete_agent()
            self._session.commit()
            return BasicResponse(message="Agente deletado com sucesso.")
        except HTTPException as e:
            self._session.rollback()
            raise e
        except Exception as e:
            self._session.rollback()
            raise HTTPException(detail="Erro interno", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _get_agent(self) -> None:
        self._agent: Agent = self._session.query(Agent).filter(Agent.id == self._agent_id).first()
        if not self._agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Agente não encontrado"
            )
    
    def _delete_agent(self) -> None:
        self._agent.enabled = False
        self._session.add(self._agent)