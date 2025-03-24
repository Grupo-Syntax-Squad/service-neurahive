from pydantic import BaseModel

class PostGroup:
    name: str

class UpdateGroupSchema:
    name: str
    enabled: bool