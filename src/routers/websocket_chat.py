from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from src.modules.ai import AiHandler
from src.modules.connection_manager import ConnectionManager
from src.schemas.chat_payload import ChatPayload

router = APIRouter(prefix="/ws")

manager = ConnectionManager()


@router.websocket("/chat")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            payload = ChatPayload(**data)
            ai_response = await AiHandler(payload.user_id, payload.message).execute()
            await manager.send_personal_message(ai_response)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast("Um usuário saiu da conexão.")
    except Exception as e:
        await manager.send_personal_message(
            f"Ocorreu um erro inesperado: {e}. Tente novamente.", websocket
        )
