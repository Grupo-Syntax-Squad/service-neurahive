from fastapi import FastAPI
from src.database.get_db import engine
from src.database.models import Base
from src.middlewares.logging import log_requests
from src.routers import (
    auth,
    example,
    user,
    group,
    agent,
    websocket_chat,
    chat,
    knowledge_base,
)
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

Base.metadata.create_all(bind=engine)


app = FastAPI()
app.middleware("http")(log_requests)
app.include_router(example.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(group.router)
app.include_router(agent.router)
app.include_router(websocket_chat.router)
app.include_router(chat.router)
app.include_router(knowledge_base.router)
