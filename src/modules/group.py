from typing import List
from fastapi.responses import JSONResponse
from database.models import Agent, Group, User
from schemas.basic_response import BasicResponse
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from schemas.group import PostGroup, UpdateGroupSchema

class CreateGroup:
    def __init__(self, session: Session, request: PostGroup):
        self.session = session
        self.request = request
    
    def execute(self) -> JSONResponse:
        group = self.create_group()
        return BasicResponse(data=group, message="Grupo criado com sucesso.", status_code=status.HTTP_201_CREATED)()
    
    def create_group(self):
        with self.session as db:
            group = Group(name=self.request.name, agents=[])
            db.add(group)
            db.commit()
            return group

class ReadGroupById:
    def __init__(self, session: Session, group_id: int):
        self.session = session
        self.group_id = group_id
    
    def execute(self) -> BasicResponse[None]:
        group = self.read_group()
        if(group):
            return BasicResponse(data = group, status_code=status.HTTP_200_OK)()
        return BasicResponse(message="Grupo não encontrado", status_code=status.HTTP_404_NOT_FOUND)()
        
    def read_group(self) -> Group:
        with self.session as db:
            return db.query(Group).get(self.group_id)

class ListGroups:
    def __init__(self, session: Session):
        self.session = session
    
    def execute(self) -> JSONResponse:
        groups = self.list_groups()
        return BasicResponse(data=groups, status_code=status.HTTP_200_OK)()
    
    def list_groups(self) -> List[Group]:
        with self.session as db:
            return db.query(Group).all()

class DeleteGroup:
    def __init__(self, session: Session, group_id: int):
        self.session = session
        self.group_id = group_id
    
    def execute(self) -> JSONResponse:
        group = self.delete_group()
        return BasicResponse(data=group, message="Grupo desabilitado com sucesso.", status_code=status.HTTP_200_OK)()
        
    def delete_group(self):
        with self.session as db:
            group: Group = db.query(Group).get(self.group_id)
            if not group:
                raise HTTPException(status_code=404, detail="Grupo não encontrado.")
            group.enabled = False
            db.commit()
            db.refresh(group)

class UpdateGroup:
    def __init__(self, session: Session, request: UpdateGroupSchema, group_id: int):
        self.session = session
        self.group_id = group_id
        self.request = request

    def execute(self) -> JSONResponse:
        group = self.update_group()
        return BasicResponse(data=group, message="Grupo atualizado com sucesso.", status_code=status.HTTP_200_OK)()
        
    def update_group(self):
        with self.session as db:
            group: Group = db.query(Group).get(self.group_id)
            if not group:
                raise HTTPException(status_code=404, detail="Grupo não encontrado.")
            group.name = self.request.name
            group.enabled = self.request.enabled
            db.commit()
            db.refresh(group)

class AddAgentsToGroup:
    def __init__(self, session: Session, request: List[int], group_id: int):
        self.session = session
        self.group_id = group_id
        self.request = request

    def execute(self) -> JSONResponse:
        group = self.add_agents_to_group()
        return BasicResponse(data=group, message="Grupo desabilitado com sucesso.", status_code=status.HTTP_200_OK)()
    
    def add_agents_to_group(self):
        with self.session as db:
            group: Group = db.query(Group).get(self.group_id)
            if not group:
                raise HTTPException(status_code=404, detail="Grupo não encontrado.")


#class RemoveAgentsFromGroup:
