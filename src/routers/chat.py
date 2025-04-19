from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.database.get_db import get_db
from src.modules.chat import CreateChat
from src.schemas.basic_response import BasicResponse
from src.schemas.chat import PostChat

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/")
async def create_chat(
    params: PostChat, session: Session = Depends(get_db)
) -> BasicResponse[None]:
    return await CreateChat(session, params).execute()
