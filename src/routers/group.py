from typing import List
from fastapi import APIRouter, Depends
from constants import Role
from database import get_db
from modules.group import AddAgentsToGroup, CreateGroup, DeleteGroup, ListGroups, ReadGroupById, RemoveAgentsFromGroup, UpdateGroup
from schemas.basic_response import BasicResponse
from schemas.group import GroupResponse, PostGroup, UpdateGroupSchema
from sqlalchemy.orm import Session
from auth import check_role, CurrentUser, get_current_user

router = APIRouter(prefix="/groups")


@router.get("/", response_model=BasicResponse[List[GroupResponse]])
def get_groups(session: Session = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)):
    check_role(current_user, [Role.ADMIN.value, Role.CURATOR.value])
    return ListGroups(session).execute()

@router.get("/{id}", response_model=BasicResponse[GroupResponse])
def get_group_by_id(id: int, session: Session = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)):
    check_role(current_user, [Role.ADMIN.value, Role.CURATOR.value])
    return ReadGroupById(session, id).execute()

@router.post("/", response_model=BasicResponse[GroupResponse])
def post_group(request: PostGroup, current_user: CurrentUser = Depends(get_current_user), session: Session = Depends(get_db)):
    check_role(current_user, [Role.ADMIN.value, Role.CURATOR.value])
    return CreateGroup(session, request).execute()

@router.delete("/{id}")
def delete_group(id: int, current_user: CurrentUser = Depends(get_current_user), session: Session = Depends(get_db)):
    check_role(current_user, [Role.ADMIN.value, Role.CURATOR.value])
    return DeleteGroup(session, id).execute()

@router.put("/{id}", response_model=BasicResponse[GroupResponse])
def update_group(id: int, request: UpdateGroupSchema, current_user: CurrentUser = Depends(get_current_user), session: Session = Depends(get_db)):
    check_role(current_user, [Role.ADMIN.value, Role.CURATOR.value])
    return UpdateGroup(session, request, id).execute()

@router.patch("/{id}/addAgents", response_model=BasicResponse[GroupResponse])
def add_agents_to_group(id: int, request: list[int], current_user: CurrentUser = Depends(get_current_user), session: Session = Depends(get_db)):
    check_role(current_user, [Role.ADMIN.value, Role.CURATOR.value])
    return AddAgentsToGroup(session, request, id).execute()

@router.patch("/{id}/removeAgents", response_model=BasicResponse[GroupResponse])
def remove_agents_from_group(id: int, request: list[int], current_user: CurrentUser = Depends(get_current_user), session: Session = Depends(get_db)):
    check_role(current_user, [Role.ADMIN.value, Role.CURATOR.value])
    return RemoveAgentsFromGroup(session, request, id).execute()
    