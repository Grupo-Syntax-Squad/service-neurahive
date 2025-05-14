from pydantic import BaseModel


class PostKnowledgeBaseResponse(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True
        from_attributes = True


class GetKnowledgeBaseResponse(BaseModel):
    id: int
    name: str
    data: dict[str, list[str]]

    class Config:
        orm_mode = True
        from_attributes = True


class GetKnowledgeBaseMetadataResponse(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True
        from_attributes = True
