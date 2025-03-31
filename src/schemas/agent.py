from pydantic import BaseModel, Field
from typing import List, Optional


class AgentResponse(BaseModel):
    id: int
    name: str
    groups: Optional[List[int]] = Field(default_factory=lambda: [])


class PostAgent(BaseModel):
    name: str
    groups: Optional[List[int]] = []
