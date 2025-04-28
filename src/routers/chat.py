from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.database.get_db import get_db
from src.modules.chat import (
    RouterCreateChat,
    RouterDeleteChat,
    RouterGetChatHistory,
    RouterGetChats,
)
from src.schemas.basic_response import BasicResponse
from src.schemas.chat import (
    GetChatHistoryRequest,
    GetChatHistoryResponse,
    GetChatsRequest,
    GetChatsResponse,
    PostChat,
)

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/")
def create_chat(
    params: PostChat, session: Session = Depends(get_db)
) -> BasicResponse[None]:
    # TODO: Implement profile validation here
    return RouterCreateChat(session, params).execute()


@router.get("/")
def get_chats(
    params: GetChatsRequest = Query(), session: Session = Depends(get_db)
) -> BasicResponse[list[GetChatsResponse]]:
    # TODO: Implement profile validation here
    return RouterGetChats(session, params).execute()


@router.delete("/")
def delete_chat(
    chat_id: int, session: Session = Depends(get_db)
) -> BasicResponse[None]:
    # TODO: Implement profile validation here
    return RouterDeleteChat(session, chat_id).execute()


@router.get("/history")
def get_chat_history(
    params: GetChatHistoryRequest = Query(), session: Session = Depends(get_db)
) -> BasicResponse[list[GetChatHistoryResponse]]:
    # TODO: Implement profile validation here
    return RouterGetChatHistory(session, params).execute()
