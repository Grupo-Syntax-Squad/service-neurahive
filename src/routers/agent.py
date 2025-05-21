from src.constants import Role
from sqlalchemy.orm import Session
from src.database.get_db import get_db
from fastapi import APIRouter, Depends, Query, UploadFile, File, Form
from src.auth.auth_utils import PermissionValidator
from src.schemas.auth import CurrentUser
from src.schemas.basic_response import BasicResponse, GetAgentBasicResponse
from src.auth.auth_utils import Auth
from src.schemas.agent import (
    AgentResponse,
    GetAgentRequest,
    GetAgentsRequest,
)
from src.modules.agent import CreateAgent, DeleteAgent, GetAgent, GetAgents, UpdateAgent
from typing import Optional, List

router = APIRouter(prefix="/agents", tags=["Agents"])


@router.get("/")
def get_agents(
    params: GetAgentsRequest = Query(),
    current_user: CurrentUser = Depends(Auth.get_current_user),
    session: Session = Depends(get_db),
) -> GetAgentBasicResponse[list[AgentResponse]]:
    PermissionValidator(current_user, [Role.ADMIN, Role.CURATOR]).execute()
    return GetAgents(session, params).execute()


@router.get("/{agent_id}")
def get_agent(
    agent_id: int,
    current_user: CurrentUser = Depends(Auth.get_current_user),
    session: Session = Depends(get_db),
) -> GetAgentBasicResponse[AgentResponse]:
    PermissionValidator(current_user, [Role.ADMIN, Role.CURATOR]).execute()
    params = GetAgentRequest(agent_id=agent_id)
    return GetAgent(session, params).execute()


@router.post("/")
async def post_agent(
    name: str = Form(...),
    theme: str = Form(...),
    behavior: Optional[str] = Form(None),
    temperature: float = Form(...),
    top_p: float = Form(...),
    image_id: int = Form(None),
    groups: Optional[List[int]] = Form(default_factory=list),
    knowledge_base_id: Optional[int] = Form(None),
    file: Optional[UploadFile] = File(None),
    knowledge_base_name: Optional[str] = Form(None),
    current_user: CurrentUser = Depends(Auth.get_current_user),
    session: Session = Depends(get_db),
) -> BasicResponse[AgentResponse]:
    PermissionValidator(current_user, [Role.ADMIN, Role.CURATOR]).execute()
    return await CreateAgent(
        session,
        name,
        theme,
        behavior,
        temperature,
        top_p,
        image_id,
        groups,
        knowledge_base_id,
        file,
        knowledge_base_name,
    ).execute()


@router.put("/{agent_id}")
async def put_agent(
    agent_id: int,
    name: str = Form(...),
    theme: str = Form(...),
    behavior: Optional[str] = Form(None),
    temperature: float = Form(...),
    top_p: float = Form(...),
    image_id: int = Form(None),
    groups: Optional[List[int]] = Form(default_factory=list),
    knowledge_base_id: Optional[int] = Form(None),
    file: Optional[UploadFile] = File(None),
    knowledge_base_name: Optional[str] = Form(None),
    current_user: CurrentUser = Depends(Auth.get_current_user),
    session: Session = Depends(get_db)
) -> BasicResponse[AgentResponse]:
    PermissionValidator(current_user, [Role.ADMIN, Role.CURATOR]).execute()
    return await UpdateAgent(
        session,
        agent_id,
        name,
        theme,
        behavior,
        temperature,
        top_p,
        image_id,
        groups,
        knowledge_base_id,
        file,
        knowledge_base_name
    ).execute()


@router.delete("/")
def delete_agent(
    agent_id: int,
    current_user: CurrentUser = Depends(Auth.get_current_user),
    session: Session = Depends(get_db),
) -> BasicResponse[None]:
    PermissionValidator(current_user, [Role.ADMIN, Role.CURATOR]).execute()
    return DeleteAgent(session, agent_id).execute()
