from fastapi import APIRouter, Depends
from constants import Role
from database import get_db
from modules.group import CreateGroup, DeleteGroup, ListGroups, ReadGroupById, UpdateGroup
from schemas.group import PostGroup, UpdateGroupSchema
from sqlalchemy.orm import Session
from auth import check_role, CurrentUser, get_current_user

router = APIRouter(prefix="/groups")


@router.get("/")
def get_groups(session: Session, current_user: CurrentUser = Depends(get_current_user)):
    check_role(current_user, Role.ADMIN.value)
    return ListGroups(session)

@router.get("/{id}")
def get_group_by_id(id: int, session: Session, current_user: CurrentUser = Depends(get_current_user)):
    check_role(current_user, Role.ADMIN.value)
    return ReadGroupById(session, id)

@router.post("/")
def post_group(request: PostGroup,  current_user: CurrentUser = Depends(get_current_user), session: Session = Depends(get_db)):
    check_role(current_user, Role.ADMIN.value)
    return CreateGroup(session, request).execute()

@router.delete("/{id}")
def post_group(id: int, current_user: CurrentUser = Depends(get_current_user), session: Session = Depends(get_db)):
    check_role(current_user, Role.ADMIN.value)
    return DeleteGroup(session, id).execute()

@router.put("/{id}")
def post_group(id: int, request: UpdateGroupSchema, current_user: CurrentUser = Depends(get_current_user), session: Session = Depends(get_db)):
    check_role(current_user, Role.ADMIN.value)
    return UpdateGroup(session, request, id).execute()