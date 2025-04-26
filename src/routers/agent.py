from src.constants import Role
from sqlalchemy.orm import Session
from src.database.get_db import get_db
from fastapi import APIRouter, Depends
from src.auth.auth_utils import PermissionValidator
from src.schemas.auth import CurrentUser
from src.schemas.basic_response import BasicResponse, GetAgentBasicResponse
from src.auth.auth_utils import Auth
from src.schemas.agent import AgentResponse, PostAgent
from src.modules.agent import CreateAgent, DeleteAgent, GetAgent, UpdateAgent

router = APIRouter(prefix="/agents", tags=["Agents"])


@router.get("/")
def get_agents(
    agent_id: int | None = None,
    current_user: CurrentUser = Depends(Auth.get_current_user),
    session: Session = Depends(get_db),
) -> GetAgentBasicResponse[list[AgentResponse] | AgentResponse]:
    PermissionValidator(current_user, [Role.ADMIN, Role.CURATOR]).execute()
    return GetAgent(session, agent_id).execute()


@router.post("/")
def post_agent(
    request: PostAgent,
    current_user: CurrentUser = Depends(Auth.get_current_user),
    session: Session = Depends(get_db),
) -> BasicResponse[AgentResponse]:
    PermissionValidator(current_user, [Role.ADMIN, Role.CURATOR]).execute()
    return CreateAgent(session, request).execute()


@router.put("/{agent_id}")
def put_agent(
    agent_id: int,
    request: PostAgent,
    current_user: CurrentUser = Depends(Auth.get_current_user),
    session: Session = Depends(get_db),
) -> BasicResponse[AgentResponse]:
    PermissionValidator(current_user, [Role.ADMIN, Role.CURATOR]).execute()
    return UpdateAgent(session, agent_id, request).execute()


@router.delete("/")
def delete_agent(
    agent_id: int,
    current_user: CurrentUser = Depends(Auth.get_current_user),
    session: Session = Depends(get_db),
) -> BasicResponse[None]:
    PermissionValidator(current_user, [Role.ADMIN, Role.CURATOR]).execute()
    return DeleteAgent(session, agent_id).execute()
