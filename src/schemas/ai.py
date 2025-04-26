from datetime import datetime
from pydantic import BaseModel


class AiResponse(BaseModel):
    answer: str
    response_date: datetime
