from datetime import datetime
from pydantic import BaseModel

from src.schemas.agent import AgentResponse


class PostUser(BaseModel):
    name: str
    email: str
    password: str
    role: list[int]
    selected_agents: list[int]

    class Config:
        orm_mode = True
        from_attributes = True


class GetUserResponse(BaseModel):
    id: int
    role: list[int]
    name: str
    email: str
    password: str
    created_at: datetime
    updated_at: datetime | None
    last_login: datetime | None
    enabled: bool
    agents: list[AgentResponse] | None

    class Config:
        orm_mode = True
        from_attributes = True


class PutUserRequest(BaseModel):
    id: int
    email: str
    password: str
    name: str
    role: list[int]
    selected_agents: list[int]

    class Config:
        orm_mode = True
        from_attributes = True
