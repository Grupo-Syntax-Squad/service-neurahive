from datetime import datetime
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from src.database.get_db import get_db
from src.modules.ai import AiHandler
from src.modules.connection_manager import ConnectionManager
from src.schemas.chat_payload import ChatPayload
from sqlalchemy.orm import Session

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
            payload = ChatPayload(**data, message_date=datetime.now())
            ai_response = AiHandler(session, payload).execute()
            await manager.send_personal_message(
                ai_response.model_dump_json(), websocket
            )
    except WebSocketDisconnect:
        # TODO: Remove this broadcast in the future
        manager.disconnect(websocket)
        await manager.broadcast("Um usuário saiu da conexão.")
    except Exception as e:
        await manager.send_personal_message(
            f"Ocorreu um erro inesperado: {e}. Tente novamente.", websocket
        )
