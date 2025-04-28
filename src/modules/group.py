from typing import List
from src.database.models import Agent, Group
from src.schemas.basic_response import BasicResponse
from src.schemas.group import GroupResponse, PostGroup, UpdateGroupSchema
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status


class CreateGroup:
    def __init__(self, session: Session, request: PostGroup):
        self.session = session
        self.request = request

    def execute(self) -> BasicResponse[GroupResponse]:
        group = self.create_group()
        return BasicResponse(data=group, message="Grupo criado com sucesso.")

    def create_group(self) -> GroupResponse:
        with self.session as db:
            group = Group(name=self.request.name, agents=[])
            db.add(group)
            db.commit()
            db.refresh(group)
            return GroupResponse.from_orm(group)


class ReadGroupById:
    def __init__(self, session: Session, group_id: int):
        self.session = session
        self.group_id = group_id

    def execute(self) -> BasicResponse[GroupResponse]:
        group = self.read_group()
        if group:
            return BasicResponse(data=group)
        raise HTTPException(
            detail="Grupo não encontrado", status_code=status.HTTP_404_NOT_FOUND
        )

    def read_group(self) -> GroupResponse | None:
        with self.session as db:
            group = db.query(Group).options(joinedload(Group.agents)).get(self.group_id)
            if group:
                return GroupResponse.from_orm(group)
            return None


class ListGroups:
    def __init__(self, session: Session):
        self.session = session

    def execute(self) -> BasicResponse[list[GroupResponse]]:
        groups = self.list_groups()
        return BasicResponse(data=[group for group in groups])

    def list_groups(self) -> list[GroupResponse]:
        with self.session as db:
            groups = db.query(Group).options(joinedload(Group.agents)).all()
            serialized_groups = [GroupResponse.from_orm(group) for group in groups]
            return serialized_groups


class DeleteGroup:
    def __init__(self, session: Session, group_id: int):
        self.session = session
        self.group_id = group_id

    def execute(self) -> BasicResponse[GroupResponse]:
        group = self.delete_group()
        return BasicResponse(data=group, message="Grupo desabilitado com sucesso.")

    def delete_group(self) -> GroupResponse:
        with self.session as db:
            group: Group = db.query(Group).get(self.group_id)  # type: ignore[assignment]
            if not group:
                raise HTTPException(status_code=404, detail="Grupo não encontrado.")
            group.enabled = False
            db.commit()
            db.refresh(group)
            return GroupResponse(**group.__dict__)


class UpdateGroup:
    def __init__(self, session: Session, request: UpdateGroupSchema, group_id: int):
        self.session = session
        self.group_id = group_id
        self.request = request

    def execute(self) -> BasicResponse[GroupResponse]:
        group = self.update_group()
        return BasicResponse(data=group, message="Grupo atualizado com sucesso.")

    def update_group(self) -> GroupResponse:
        with self.session as db:
            group: Group = (
                db.query(Group).options(joinedload(Group.agents)).get(self.group_id)  # type: ignore[assignment]
            )
            if not group:
                raise HTTPException(status_code=404, detail="Grupo não encontrado.")
            group.name = self.request.name
            group.enabled = self.request.enabled
            db.commit()
            db.refresh(group)
            return GroupResponse.from_orm(group)


class AddAgentsToGroup:
    def __init__(self, session: Session, request: List[int], group_id: int):
        self.session = session
        self.group_id = group_id
        self.request = request

    def execute(self) -> BasicResponse[GroupResponse]:
        group = self.add_agents_to_group()
        return BasicResponse(data=group, message="Agentes adicionados com sucesso.")

    def add_agents_to_group(self) -> GroupResponse:
        with self.session as db:
            group: Group = (
                db.query(Group).options(joinedload(Group.agents)).get(self.group_id)  # type: ignore[assignment]
            )
            if not group:
                raise HTTPException(status_code=404, detail="Grupo não encontrado.")
            agents: List[Agent] = (
                db.query(Agent).filter(Agent.id.in_(self.request)).all()
            )
            if len(agents) != len(self.request):
                raise HTTPException(
                    status_code=404, detail="Alguns agentes não foram encontrados"
                )
            for agent in agents:
                if agent not in group.agents:
                    group.agents.append(agent)
            db.commit()
            return GroupResponse.from_orm(group)


class RemoveAgentsFromGroup:
    def __init__(self, session: Session, request: List[int], group_id: int):
        self.session = session
        self.group_id = group_id
        self.request = request

    def execute(self) -> BasicResponse[GroupResponse]:
        group = self.remove_agents_from_group()
        return BasicResponse(data=group, message="Agentes removidos com sucesso.")

    def remove_agents_from_group(self) -> GroupResponse:
        with self.session as db:
            group: Group = (
                db.query(Group).options(joinedload(Group.agents)).get(self.group_id)  # type: ignore[assignment]
            )
            if not group:
                raise HTTPException(status_code=404, detail="Grupo não encontrado.")
            agents: List[Agent] = (
                db.query(Agent).filter(Agent.id.in_(self.request)).all()
            )
            if len(agents) != len(self.request):
                raise HTTPException(
                    status_code=404, detail="Alguns agentes não foram encontrados"
                )
            for agent in agents:
                if agent in group.agents:
                    group.agents.remove(agent)
                else:
                    raise HTTPException(
                        status_code=400, detail="Agente não está associado a este grupo"
                    )
            db.commit()
            return GroupResponse.from_orm(group)
