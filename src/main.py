from fastapi import FastAPI
from database import engine
from database.models import Base
from routers import example, user

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(example.router)
app.include_router(user.router)
