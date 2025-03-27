from fastapi import FastAPI
from src.routers import auth, example, user

app = FastAPI()
app.include_router(example.router)
app.include_router(user.router)
app.include_router(auth.router)
