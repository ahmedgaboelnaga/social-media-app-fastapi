from fastapi import FastAPI
from contextlib import asynccontextmanager

from .routers import auth, post, user, vote
from .core import create_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(vote.router)


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Welcome to my API"}
