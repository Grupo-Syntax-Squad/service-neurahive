from pydantic import BaseModel


class AiResponse(BaseModel):
    answer: str
    response_date: int  # NOTE: UNIX TIMESTAMP
