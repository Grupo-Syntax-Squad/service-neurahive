from typing import List
from fastapi import APIRouter, Depends
from src.auth.auth_utils import Auth, PermissionValidator
from src.constants import Role
from src.database.get_db import get_db
from src.modules.group import (
    AddAgentsToGroup,
    CreateGroup,
    DeleteGroup,
    ListGroups,
    ReadGroupById,
    RemoveAgentsFromGroup,
    UpdateGroup,
)
from src.schemas.auth import CurrentUser
from src.schemas.basic_response import BasicResponse
from src.schemas.group import GroupResponse, PostGroup, UpdateGroupSchema
from sqlalchemy.orm import Session

router = APIRouter(prefix="/groups")


@router.get("/", response_model=BasicResponse[List[GroupResponse]])
def get_groups(
    session: Session = Depends(get_db),
    current_user: CurrentUser = Depends(Auth.get_current_user),
) -> BasicResponse[list[GroupResponse]]:
    PermissionValidator(current_user, [Role.ADMIN, Role.CURATOR]).execute()
    return ListGroups(session).execute()()


@router.get("/{id}", response_model=BasicResponse[GroupResponse])
def get_group_by_id(
    id: int,
    session: Session = Depends(get_db),
    current_user: CurrentUser = Depends(Auth.get_current_user),
) -> BasicResponse[GroupResponse]:
    PermissionValidator(current_user, [Role.ADMIN, Role.CURATOR]).execute()
    return ReadGroupById(session, id).execute()()


@router.post("/", response_model=BasicResponse[GroupResponse])
def post_group(
    request: PostGroup,
    current_user: CurrentUser = Depends(Auth.get_current_user),
    session: Session = Depends(get_db),
) -> BasicResponse[GroupResponse]:
    PermissionValidator(current_user, [Role.ADMIN, Role.CURATOR]).execute()
    return CreateGroup(session, request).execute()()


@router.delete("/{id}")
def delete_group(
    id: int,
    current_user: CurrentUser = Depends(Auth.get_current_user),
    session: Session = Depends(get_db),
) -> BasicResponse[GroupResponse]:
    PermissionValidator(current_user, [Role.ADMIN, Role.CURATOR]).execute()
    return DeleteGroup(session, id).execute()()


@router.put("/{id}", response_model=BasicResponse[GroupResponse])
def update_group(
    id: int,
    request: UpdateGroupSchema,
    current_user: CurrentUser = Depends(Auth.get_current_user),
    session: Session = Depends(get_db),
) -> BasicResponse[GroupResponse]:
    PermissionValidator(current_user, [Role.ADMIN, Role.CURATOR]).execute()
    return UpdateGroup(session, request, id).execute()()


@router.patch("/{id}/addAgents", response_model=BasicResponse[GroupResponse])
def add_agents_to_group(
    id: int,
    request: list[int],
    current_user: CurrentUser = Depends(Auth.get_current_user),
    session: Session = Depends(get_db),
) -> BasicResponse[GroupResponse]:
    PermissionValidator(current_user, [Role.ADMIN, Role.CURATOR]).execute()
    return AddAgentsToGroup(session, request, id).execute()()


@router.patch("/{id}/removeAgents", response_model=BasicResponse[GroupResponse])
def remove_agents_from_group(
    id: int,
    request: list[int],
    current_user: CurrentUser = Depends(Auth.get_current_user),
    session: Session = Depends(get_db),
) -> BasicResponse[GroupResponse]:
    PermissionValidator(current_user, [Role.ADMIN, Role.CURATOR]).execute()
    return RemoveAgentsFromGroup(session, request, id).execute()()
