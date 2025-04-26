from datetime import datetime
from pydantic import BaseModel


class ChatPayload(BaseModel):
    chat_id: int
    message: str
    message_date: datetime
