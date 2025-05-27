from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class GeneralStatisticsResponse(BaseModel):
    total_agents: int
    total_users: int
    total_conversations: int
    total_messages: int
    total_agents_with_recent_iteractions: int
    total_users_with_recent_iteractions: int
    most_active_agent_id: int
    most_active_agent_name: str

    class Config:
        orm_mode = True
        from_attributes = True


class GeneralStatisticsRequest(BaseModel):
    start_date: str | None = None
    end_date: str | None = None
    user_id: int | None = None
    agent_id: int | None = None


class UserInteractionsRequest(BaseModel):
    user_id: int
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    agent_id: Optional[int] = None


class UserInteractionsResponse(BaseModel):
    user_id: int
    user_name: str
    user_iteractions: int
    iteractions_with_agents: int
    agent_last_iteraction: Optional[datetime]
