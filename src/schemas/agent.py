from pydantic import BaseModel, Field
from typing import List, Optional


class GetAgentsRequest(BaseModel):
    user_id: int | None = None
    disabled_agents: bool = False


class GetAgentRequest(BaseModel):
    agent_id: int


class AgentResponse(BaseModel):
    id: int
    name: str
    theme: str
    behavior: str | None
    temperature: float
    top_p: float
    image_id: int | None
    groups: Optional[List[int]] = Field(default_factory=lambda: [])
    knowledge_base_id: Optional[int]
    enabled: bool

    class Config:
        orm_mode = True
        from_attributes = True


class PostAgent(BaseModel):
    name: str
    theme: str
    behavior: Optional[str] = None
    temperature: float = Field(default=0.5)
    top_p: float = Field(default=0.5)
    groups: Optional[List[int]] = []
    knowledge_base_id: Optional[int]
    enabled: bool

    class Config:
        orm_mode = True
        from_attributes = True
