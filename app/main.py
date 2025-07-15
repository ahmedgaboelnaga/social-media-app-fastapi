from fastapi import FastAPI, status, HTTPException
from fastapi.params import Depends
from pydantic import BaseModel
from typing import Any
import psycopg
from psycopg.rows import dict_row
# from psycopg2.extras import RealDictCursor # This is meant for v.2
# import time
app = FastAPI()

DB_CONFIG: dict[str, Any] = {
    "host": "localhost",
    "port": 5432,
    "dbname": "fastapi",
    "user": "postgres",
    "password": "645798",
    "row_factory": dict_row
}


def get_connection():
    conn = psycopg.connect(**DB_CONFIG)
    try:
        yield conn
    finally:
        conn.close()


def get_cursor(conn=Depends(get_connection)):
    cursor = conn.cursor()
    try:
        yield cursor
        conn.commit()  # Optional: only commit if needed
    finally:
        cursor.close()


# def get_cursor():
#     conn = psycopg.connect(**DB_CONFIG)
#     cursor = conn.cursor()
#     try:
#         yield cursor
#         conn.commit()
#     finally:
#         cursor.close()
#         conn.close()


# # This is how to define global connection
# while True:
#     try:
#         conn = psycopg.connect(**DB_CONFIG)
#         cur = conn.cursor()
#         print("Database connection was successful.")
#         break
#     except Exception as e:
#         print("Database connection Failed")
#         print("Error: ", e)
#         time.sleep(2) # This will try to wait for 2 seconds before trying to reconnect, but it will not help if there is an issue with the
#                       # credentials, but it works if there is a problem with the connection or a network failure issue


class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    # rating: Optional[int] = None # This helps us to give it None if we don't have an integer instead of passing a default int like zero or True for bool
    # rating: int | None = None
    rating: int | None = None

# id: int = 2
# all_posts: list[dict[str, Any]] = [
#         {"title": "Post1", "content": "content of post1", "published": True, "rating": None, "id": 1},
#         {"title": "Favorite Food", "content": "I like pizza!", "published": True, "rating": None, "id": 2}
#     ]

@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Welcome to my API"}


@app.get("/posts")
async def get_posts(cur=Depends(get_cursor)) -> dict[str, Any]:
    cur.execute("SELECT * FROM posts;")
    posts: list[dict[str, Any]] = cur.fetchall()
    if not posts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No posts found")
    return {"data": posts}


@app.get("/posts/latest")
async def get_latest_post(cur=Depends(get_cursor)) -> dict[str, Any]:
    cur.execute("SELECT * FROM posts ORDER BY created_at DESC LIMIT 1;")
    post = cur.fetchone()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="There are no posts yet.")
    return {"data": post}


# def get_post_by_id(id: int) -> dict[str, Any] |None:
#     for post in all_posts:
#         if post["id"] == id:
#             return post
#     return None


# def search_index(id: int) -> int | None:
#     for i, post in enumerate(all_posts):
#         if post['id'] == id:
#             return i
#     return None


# def search_index(id: int) -> int | None:
#     low: int = 0
#     high: int= len(all_posts) - 1
#     while low <= high:
#         # mid: int = (low + high) // 2
#         mid: int = low + ((high - low) // 2)
#         guess:dict[str, Any] = all_posts[mid]
#         if guess["id"] == id:
#             return mid
#         elif guess["id"] < id:
#             low: int = mid + 1
#         else:
#             high: int = mid - 1
#     return None


@app.get("/posts/{post_id}")
async def get_post(post_id: int, cur=Depends(get_cursor)) -> dict[str, Any]:
    cur.execute("SELECT * FROM posts WHERE id = %s;",
                (post_id,))
    post = cur.fetchone()
    if not post:
        #     # response.status_code = status.HTTP_404_NOT_FOUND
        #     # return {"message": f"Post with id: {id} was not found!"}
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id: {post_id} was not found")
    return {"data": post}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
async def create_post(post: Post, cur=Depends(get_cursor)) -> dict[str, Any]:
    cur.execute("INSERT INTO posts (title, content, published, rating) VALUES (%s, %s, %s, %s) RETURNING *;",
                (post.title, post.content, post.published, post.rating))
    new_post: dic[str, Any] = cur.fetchone()
    if not new_post:
        raise HTTPException(status_code=500, detail="Failed to create post")
    return {"data": new_post}


@app.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: int, cur=Depends(get_cursor)) -> None:
    cur.execute("DELETE FROM posts WHERE id = %s RETURNING *;",
                (post_id,))
    deleted_post:dict[str, Any] = cur.fetchone()
    if not deleted_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The post with id: {post_id} wasn't found.")
    return


@app.put("/posts/{post_id}")
async def update_post(post_id: int, post: Post, cur=Depends(get_cursor)) -> dict[str, Any]:
    cur.execute(
        "UPDATE posts SET title = %s, content = %s, published = %s, rating = %s WHERE id = %s RETURNING *;",
        (post.title, post.content, post.published, post.rating, post_id)
    )
    updated_post: dict[str, Any] = cur.fetchone()
    if not updated_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The post with id: {post_id} wasn't found.")
    return {"data": updated_post}
