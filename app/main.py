from typing import Any, List
from fastapi import FastAPI, status, HTTPException
from sqlmodel import desc
from . import schemas
from . import models
from .database import engine, DBSession
from .db_driver import Cursor

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Welcome to my API"}


@app.get("/posts", response_model=List[schemas.PostResponse])
async def get_posts(db: DBSession) -> List[models.Post]:
    posts: List[models.Post] = db.query(models.Post).all()
    if not posts:   
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No Posts Found!")
    return posts


@app.get("/posts/latest", response_model=schemas.PostResponse)
async def get_latest_post(db: DBSession) -> models.Post:
    post_query = db.query(models.Post).order_by(desc(models.Post.created_at))
    post: models.Post | None = post_query.first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="There are no posts yet.")
    return post


@app.get("/posts/{post_id}", response_model=schemas.PostResponse)
async def get_post(post_id: int, db: DBSession) -> models.Post:
    post: models.Post | None = db.query(models.Post).filter_by(id=post_id).first()
    if not post:
        #     # response.status_code = status.HTTP_404_NOT_FOUND
        #     # return {"message": f"Post with id: {id} was not found!"}
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id: {post_id} was not found")
    return post


@app.post("/posts", status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse)
async def create_post(post: schemas.PostCreate, db: DBSession) -> models.Post:
    new_post: models.Post = models.Post(**post.model_dump())
    try:
        db.add(new_post)
        db.commit()
        db.refresh(new_post)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    return new_post


@app.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: int, db: DBSession) -> None:
    post_query = db.query(models.Post).filter_by(id=post_id)
    post: models.Post | None = post_query.first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The post with id: {post_id} wasn't found.")
    post_query.delete(synchronize_session=False)
    db.commit()
    return


@app.put("/posts/{post_id}", response_model=schemas.PostResponse)
async def update_post(post_id: int, updated_post: schemas.PostCreate, db: DBSession) -> models.Post:
    post_query = db.query(models.Post).filter_by(id=post_id)
    post: models.Post | None = post_query.first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The post with id: {post_id} wasn't found.")
    try:
        post_query.update(updated_post.model_dump(), synchronize_session=False)
        db.commit()
        db.refresh(post)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Databaase Error {e}")
    return post
