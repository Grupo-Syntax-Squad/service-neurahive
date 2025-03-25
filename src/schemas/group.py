from pydantic import BaseModel
from typing import List

class PostGroup(BaseModel):
    name: str

    class Config:
        orm_mode = True
        from_attributes = True

class UpdateGroupSchema(BaseModel):
    name: str
    enabled: bool

    class Config:
        orm_mode = True
        from_attributes = True

class AgentResponse(BaseModel):
    id: int
    name: str
    
    class Config:
        orm_mode = True
        from_attributes = True

class GroupResponse(BaseModel):
    id: int
    name: str
    enabled: bool
    agents: List[AgentResponse]
    
    class Config:
        orm_mode = True
        from_attributes = True
