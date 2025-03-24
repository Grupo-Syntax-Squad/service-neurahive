from pydantic import BaseModel


class PostUser(BaseModel):
    email: str
    password: str
    role: list[int]
    name: str
