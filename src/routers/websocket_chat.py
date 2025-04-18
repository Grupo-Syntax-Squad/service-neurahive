from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from src.modules.connection_manager import ConnectionManager

router = APIRouter(prefix="/ws")

manager = ConnectionManager()


@router.websocket("/chat")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"Mensagem recebida: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast("Um usuário saiu da conexão.")
