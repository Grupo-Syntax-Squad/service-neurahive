from pydantic import BaseModel, Field
from typing import List, Optional


class AgentResponse(BaseModel):
    id: int
    name: str
    theme: str
    behavior: str
    temperature: float
    top_p: float
    groups: Optional[List[int]] = Field(default_factory=lambda: [])

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

    class Config:
        orm_mode = True
        from_attributes = True
