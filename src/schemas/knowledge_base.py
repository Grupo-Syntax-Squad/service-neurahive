from pydantic import BaseModel
from typing import Dict, Any


class PostKnowledgeBaseResponse(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True
        from_attributes = True


class GetKnowledgeBaseResponse(BaseModel):
    id: int
    name: str
    data: Dict[str, Any]

    class Config:
        orm_mode = True
        from_attributes = True


class GetKnowledgeBaseMetadataResponse(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True
        from_attributes = True
