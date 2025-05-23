from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class CurrentUser(BaseModel):
    id: int
    email: str
    name: str
    role: list[int]
    enabled: bool

    class Config:
        from_attributes = True
