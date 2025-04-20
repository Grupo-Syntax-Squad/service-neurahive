from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.database.get_db import get_db
from src.modules.chat import RouterCreateChat, RouterDeleteChat, RouterGetChats
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


@router.delete("/")
def delete_chat(
    chat_id: int, session: Session = Depends(get_db)
) -> BasicResponse[None]:
    return RouterDeleteChat(session, chat_id).execute()
