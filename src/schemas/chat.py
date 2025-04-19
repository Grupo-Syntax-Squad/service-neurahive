from pydantic import BaseModel


class PostChat(BaseModel):
    user_id: int
    agent_id: int
