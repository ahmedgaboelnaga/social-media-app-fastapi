from typing import Any
from fastapi import FastAPI, status, HTTPException
from pydantic import BaseModel
from . import models # I don't know what is the difference between both because .models in fact imoprt Base from .database
from .database import engine, DBSession
from .db_driver import Cursor

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    # rating: Optional[int] = None # This helps us to give it None if we don't have an integer instead of passing a default int like zero or True for bool
    # rating: int | None = None
    rating: int | None = None


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Welcome to my API"}


@app.get("/sqlalchemy")
async def test(db: DBSession):
    posts = db.query(models.Post).all()
    if not posts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No Posts Found!")
    return {"data": posts}


@app.get("/posts")
async def get_posts(cur: Cursor) -> dict[str, Any]:
    cur.execute("SELECT * FROM posts;")
    posts: list[dict[str, Any]] = cur.fetchall()
    if not posts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No posts found")
    return {"data": posts}


@app.get("/posts/latest")
async def get_latest_post(cur: Cursor) -> dict[str, Any]:
    cur.execute("SELECT * FROM posts ORDER BY created_at DESC LIMIT 1;")
    post: dict[str, Any] = cur.fetchone()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="There are no posts yet.")
    return {"data": post}


@app.get("/posts/{post_id}")
async def get_post(post_id: int, cur: Cursor) -> dict[str, Any]:
    cur.execute("SELECT * FROM posts WHERE id = %s;",
                (post_id,))
    post: dict[str, Any] = cur.fetchone()
    if not post:
        #     # response.status_code = status.HTTP_404_NOT_FOUND
        #     # return {"message": f"Post with id: {id} was not found!"}
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id: {post_id} was not found")
    return {"data": post}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
async def create_post(post: Post, cur: Cursor) -> dict[str, Any]:
    cur.execute("INSERT INTO posts (title, content, published, rating) VALUES (%s, %s, %s, %s) RETURNING *;",
                (post.title, post.content, post.published, post.rating))
    new_post: dict[str, Any] = cur.fetchone()
    if not new_post:
        raise HTTPException(status_code=500, detail="Failed to create post")
    return {"data": new_post}


@app.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: int, cur: Cursor) -> None:
    cur.execute("DELETE FROM posts WHERE id = %s RETURNING *;",
                (post_id,))
    deleted_post:dict[str, Any] = cur.fetchone()
    if not deleted_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The post with id: {post_id} wasn't found.")
    return


@app.put("/posts/{post_id}")
async def update_post(post_id: int, post: Post, cur: Cursor) -> dict[str, Any]:
    cur.execute(
        "UPDATE posts SET title = %s, content = %s, published = %s, rating = %s WHERE id = %s RETURNING *;",
        (post.title, post.content, post.published, post.rating, post_id)
    )
    updated_post: dict[str, Any] = cur.fetchone()
    if not updated_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The post with id: {post_id} wasn't found.")
    return {"data": updated_post}
