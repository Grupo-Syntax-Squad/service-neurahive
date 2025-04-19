from pydantic import BaseModel


class ChatPayload(BaseModel):
    user_id: int
    message: str
