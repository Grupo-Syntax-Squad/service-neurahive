from pydantic import BaseModel, Field
from typing import List, Optional


class AgentResponse(BaseModel):
    id: int
    name: str
    groups: Optional[List[int]] = Field(default_factory=lambda: [])

    class Config:
        orm_mode = True
        from_attributes = True


class PostAgent(BaseModel):
    name: str
    groups: Optional[List[int]] = []

    class Config:
        orm_mode = True
        from_attributes = True
