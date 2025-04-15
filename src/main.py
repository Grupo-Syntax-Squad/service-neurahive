from fastapi import FastAPI, WebSocket, WebSocketDisconnect, WebSocketException, status
from src.database.get_db import engine
from src.database.models import Base
from src.routers import auth, example, user, group, agent

Base.metadata.create_all(bind=engine)


app = FastAPI()
app.include_router(example.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(group.router)
app.include_router(agent.router)


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"Mensagem recebida: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast("Um usuário saiu da conexão.")
