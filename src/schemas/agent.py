from pydantic import BaseModel
from typing import List, Optional


class AgentResponse(BaseModel):
    id: int
    name: str
    groups: Optional[List[int]] = []


class PostAgent(BaseModel):
    name: str
    groups: Optional[List[int]] = []
