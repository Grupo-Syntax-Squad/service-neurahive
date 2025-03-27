from datetime import datetime
from pydantic import BaseModel


class PostUser(BaseModel):
    name: str
    email: str
    password: str
    role: list[int]


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


class PutUserRequest(BaseModel):
    id: int
    email: str
    password: str
    name: str
    role: list[int]
