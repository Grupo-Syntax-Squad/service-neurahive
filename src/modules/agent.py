from src.schemas.basic_response import BasicResponse
from src.database.models import Agent, Group
from src.schemas.agent import AgentResponse, PostAgent
from sqlalchemy.orm import Session
from fastapi import HTTPException, status


class CreateAgent:
    def __init__(self, session: Session, request: PostAgent):
        self.session = session
        self.request = request

    def execute(self) -> BasicResponse[AgentResponse]:
        agent = self.create_agent()
        return BasicResponse(
            data=agent,
            message="Agent created successfully.",
            status_code=status.HTTP_201_CREATED,
        )

    def create_agent(self) -> AgentResponse:
        with self.session as db:
            agent = Agent(name=self.request.name)

            if self.request.groups:
                groups = db.query(Group).filter(Group.id.in_(self.request.groups)).all()

                if len(groups) != len(self.request.groups):
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="One or more groups not found"
                    )
                agent.groups = groups

            db.add(agent)
            db.commit()
            db.refresh(agent)

            return AgentResponse(
                id=agent.id,
                name=agent.name,
                groups=[group.id for group in agent.groups]
            )


class GetAgent:
    def __init__(self, session: Session, agent_id: int | None):
        self._session = session
        self._agent_id = agent_id

    def execute(self) -> BasicResponse[AgentResponse]:
        agent_data = self._get_agent()
        return BasicResponse(data=agent_data)

    def _get_agent(self) -> AgentResponse:
        if self._agent_id:
            agent = self._session.query(Agent).filter(Agent.id == self._agent_id).first()
            if not agent:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
            return AgentResponse(id=agent.id, name=agent.name, groups=[group.id for group in agent.groups])

        agents = self._session.query(Agent).all()
        return [
            AgentResponse(id=agent.id, name=agent.name, groups=[group.id for group in agent.groups])
            for agent in agents
        ]


class UpdateAgent:
    def __init__(self, session: Session, agent_id: int, request: PostAgent) -> None:
        self.session = session
        self.agent_id = agent_id
        self.request = request

    def execute(self) -> BasicResponse[AgentResponse]:
        agent = self.update_agent()
        return BasicResponse(
            data=agent,
            message="Agent updated successfully.",
            status_code=status.HTTP_200_OK,
        )

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
                        detail="One or more groups not found"
                    )
                agent.groups = groups

            db.commit()
            db.refresh(agent)

            return AgentResponse(
                id=agent.id,
                name=agent.name,
                groups=[group.id for group in agent.groups]
            )


class DeleteAgent:
    def __init__(self, session: Session, agent_id: int):
        self._session = session
        self._agent_id = agent_id

    def execute(self) -> BasicResponse[None]:
        agent = self._session.query(Agent).filter(Agent.id == self._agent_id).first()
        if not agent:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")

        # Removendo o agente do banco de dados
        self._session.delete(agent)
        self._session.commit()

        return BasicResponse(message="Agent deleted successfully.")