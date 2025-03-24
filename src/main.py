from fastapi import FastAPI
from src.database.get_db import engine
from src.database.models import Base
from src.routers import auth, example, user

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(example.router)
app.include_router(user.router)
app.include_router(auth.router)
