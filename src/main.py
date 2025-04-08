from fastapi import FastAPI
from src.database.get_db import async_engine
from src.database.models import Base
from src.routers import auth, example, user, group, agent

Base.metadata.create_all(bind=async_engine)


app = FastAPI()
app.include_router(example.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(group.router)
app.include_router(agent.router)
