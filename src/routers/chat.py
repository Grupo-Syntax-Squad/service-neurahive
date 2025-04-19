from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.database.get_db import get_db
from src.modules.chat import RouterCreateChat, RouterGetChats
from src.schemas.basic_response import BasicResponse
from src.schemas.chat import GetChatsRequest, GetChatsResponse, PostChat

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/")
def create_chat(
    params: PostChat, session: Session = Depends(get_db)
) -> BasicResponse[None]:
    return RouterCreateChat(session, params).execute()


@router.get("/")
def get_chats(
    params: GetChatsRequest = Query(), session: Session = Depends(get_db)
) -> BasicResponse[list[GetChatsResponse]]:
    return RouterGetChats(session, params).execute()
