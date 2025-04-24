from fastapi import APIRouter, UploadFile, File, Depends, Form
from sqlalchemy.orm import Session
from typing import List
from src.auth.auth_utils import Auth, PermissionValidator
from src.constants import Role
from src.schemas.auth import CurrentUser
from src.schemas.basic_response import BasicResponse
from src.database.get_db import get_db
from src.schemas.knowledge_base import PostKnowledgeBaseResponse, GetKnowledgeBaseResponse, GetKnowledgeBaseMetadataResponse
from src.modules.knowledge_base import ReadKnowledgeBase, UploadKnowledgeBase, ListKnowledgeBases


router = APIRouter(prefix="/knowledge-base", tags=["Knowledge Base"])


@router.post("/")
async def upload_knowledge_base(
    file: UploadFile = File(...),
    name: str = Form(...),
    current_user: CurrentUser = Depends(Auth.get_current_user),
    session: Session = Depends(get_db)
) -> PostKnowledgeBaseResponse:
    PermissionValidator(current_user, [Role.ADMIN, Role.CURATOR]).execute()
    return await UploadKnowledgeBase(file, name, session).execute()()

@router.get("/{id}", response_model=BasicResponse[GetKnowledgeBaseResponse])
def get_knowledge_base(
    id: int,
    session: Session = Depends(get_db),
    current_user: CurrentUser = Depends(Auth.get_current_user),
) -> BasicResponse[GetKnowledgeBaseResponse]:
    PermissionValidator(current_user, [Role.ADMIN, Role.CURATOR]).execute()
    return ReadKnowledgeBase(session, id).execute()()

@router.get("/", response_model=BasicResponse[List[GetKnowledgeBaseMetadataResponse]])
def get_knowledge_base_metadata(
    session: Session = Depends(get_db),
    current_user: CurrentUser = Depends(Auth.get_current_user),
) -> BasicResponse[List[GetKnowledgeBaseMetadataResponse]]:
    PermissionValidator(current_user, [Role.ADMIN, Role.CURATOR]).execute()
    return ListKnowledgeBases(session).execute()
