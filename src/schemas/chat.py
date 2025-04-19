from pydantic import BaseModel


class PostChat(BaseModel):
    user_id: int
    agent_id: int


class GetChatsRequest(BaseModel):
    enabled: bool | None = True
    user_id: int | None = None
    agent_id: int | None = None


class GetChatsResponse(BaseModel):
    id: int
    user_id: int
    agent_id: int
    enabled: bool
