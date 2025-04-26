from datetime import datetime
from fastapi import (
    APIRouter,
    Depends,
    WebSocket,
    WebSocketDisconnect,
    WebSocketException,
    status,
)
from src.database.get_db import get_db
from src.modules.websocket_chat import AiHandler
from src.modules.connection_manager import ConnectionManager
from src.schemas.chat_payload import ChatPayload
from sqlalchemy.orm import Session
from pydantic import ValidationError

router = APIRouter(prefix="/ws")

manager = ConnectionManager()


@router.websocket("/chat")
async def websocket_endpoint(
    websocket: WebSocket, session: Session = Depends(get_db)
) -> None:
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            try:
                payload = ChatPayload(**data, message_date=datetime.now())
            except ValidationError:
                raise WebSocketException(
                    reason="Dados recebidos não estão de acordo com o esperado!",
                    code=status.WS_1003_UNSUPPORTED_DATA,
                )
            ai_response = AiHandler(session, payload).execute()
            await manager.send_personal_message(
                ai_response.model_dump_json(), websocket
            )
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except WebSocketException as we:
        await websocket.close(code=we.code, reason=we.reason)
    except Exception as e:
        await manager.send_personal_message(
            f"Ocorreu um erro inesperado: {e}. Tente novamente.", websocket
        )
