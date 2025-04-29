from sqlalchemy import select
from src.schemas.basic_response import BasicResponse, GetAgentBasicResponse
from src.database.models import Agent, Group
from src.schemas.agent import AgentResponse, PostAgent
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Union


class CreateAgent:
    def __init__(self, session: Session, request: PostAgent):
        self.session = session
        self.request = request

    def execute(self) -> BasicResponse[AgentResponse]:
        try:
            self._verify_if_knowledge_base_already_have_a_agent()
            agent = self.create_agent()
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
        query = select(Agent).where(
            Agent.knowledge_base_id == self.request.knowledge_base_id
        )
        result = self.session.execute(query)
        if result.scalars().first() is not None:
            raise HTTPException(
                detail="Base de conhecimento já vinculada a outro agente!",
                status_code=status.HTTP_409_CONFLICT,
            )

    def create_agent(self) -> AgentResponse:
        with self.session as db:
            behavior = self.request.behavior or (
                "Responda de forma clara, útil e educada. Varie o estilo mantendo o sentido original. "
                "Use uma linguagem acessível, mas mantenha profissionalismo."
            )
            agent = Agent(
                name=self.request.name,
                behavior=behavior,
                theme=self.request.theme,
                temperature=self.request.temperature,
                top_p=self.request.top_p,
                knowledge_base_id=self.request.knowledge_base_id,
            )

            if self.request.groups:
                groups = db.query(Group).filter(Group.id.in_(self.request.groups)).all()

                if len(groups) != len(self.request.groups):
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="One or more groups not found",
                    )
                agent.groups = groups

            db.add(agent)
            db.flush()
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


class GetAgent:
    def __init__(self, session: Session, agent_id: int | None):
        self._session = session
        self._agent_id = agent_id

    def execute(
        self,
    ) -> GetAgentBasicResponse[Union[AgentResponse, list[AgentResponse]]]:
        agent_data = self._get_agent()
        return GetAgentBasicResponse(data=agent_data)

    def _get_agent(self) -> list[AgentResponse] | AgentResponse:
        if self._agent_id:
            agent = (
                self._session.query(Agent).filter(Agent.id == self._agent_id).first()
            )
            if not agent:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found"
                )
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

        agents = self._session.query(Agent).all()
        return [
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
            for agent in agents
        ]


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
