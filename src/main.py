import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from src.database.get_db import engine
from src.database.models import Base
from src.middlewares.logging import log_requests
from src.routers import (
    agent,
    auth,
    chat,
    example,
    group,
    knowledge_base,
    statistics,
    user,
    websocket_chat,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

Base.metadata.create_all(bind=engine)


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*"
    ],  # << Permite requisições de qualquer origem (útil para testes, mas depois troque por domínios específicos)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", include_in_schema=False)
def index() -> RedirectResponse:
    return RedirectResponse("/docs")


app.middleware("http")(log_requests)
app.include_router(example.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(group.router)
app.include_router(agent.router)
app.include_router(websocket_chat.router)
app.include_router(chat.router)
app.include_router(knowledge_base.router)
app.include_router(statistics.router)
