from fastapi import FastAPI
from contextlib import asynccontextmanager
from . import models
from .routers import auth, post, user


@asynccontextmanager
async def lifespan(app: FastAPI):
    models.create_tables()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Welcome to my API"}
