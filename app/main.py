from fastapi import FastAPI, Response, status, HTTPException
from pydantic import BaseModel
from typing import Any, Union
import psycopg2
from psycopg2.extras import RealDictCursor
import time

app = FastAPI()

id: int = 2
class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    # rating: Optional[int] = None # This helps us to give it None if we don't have an integer instead of passing a default int like zero or True for bool
    # rating: int | None = None
    rating: Union[int, None] = None

while True:
    try:
        conn = psycopg2.connect(
            host='localhost',
            database='fastapi',
            user= 'postgres',
            password='645798',
            cursor_factory=RealDictCursor)
    
        cur = conn.cursor()
        print("Database connection was successful.")
        break
    except Exception as e:
        print("Database connection Failed")
        print("Error: ", e)
        time.sleep(2) # This will try to wait for 2 seconds before trying to reconnect, but it will not help if there is an issue with the
                      # credentials, but it works if there is a problem with the connection or a network failure issue

all_posts: list[dict[str, Any]] = [
        {"title": "Post1", "content": "content of post1", "published": True, "rating": None, "id": 1},
        {"title": "Favorite Food", "content": "I like pizza!", "published": True, "rating": None, "id": 2}
    ]

@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Welcome to my API"}


@app.get("/posts")
async def get_posts():
    cur.execute("SELECT * FROM posts;")
    posts: list[tuple[Any,...]] = cur.fetchall()
    if not posts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No posts found")
    conn.commit()
    return {"data": posts}


@app.get("/posts/latest")
async def get_latest_post() -> dict[str, dict[str, Any]]:
    cur.execute
    if not all_posts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="There are no posts yet.")
    return {"data": all_posts[-1]}


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


def search_index(id: int) -> int | None:
    low: int = 0
    high: int= len(all_posts) - 1
    while low <= high:
        # mid: int = (low + high) // 2
        mid: int = low + ((high - low) // 2)
        guess:dict[str, Any] = all_posts[mid]
        if guess["id"] == id:
            return mid
        elif guess["id"] < id:
            low: int = mid + 1
        else:
            high: int = mid - 1
    return None
    

@app.get("/posts/{id}")
async def get_posts_by_id(id: int, response: Response) -> dict[str, dict[str, Any]]:
    post_index: int | None = search_index(id)
    if post_index is None:
        # response.status_code = status.HTTP_404_NOT_FOUND
        # return {"message": f"Post with id: {id} was not found!"}
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id: {id} was not found!")
    
    post: dict[str, Any] = all_posts[post_index]
    return {"data": post}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(post: Post):
    cur.execute("INSERT INTO posts (title, content, published, rating) VALUES (%s, %s, %s, %s) RETURNING *;", (post.title, post.content, post.published, post.rating))
    new_post = cur.fetchone()
    conn.commit()

    if not new_post:
        raise HTTPException(status_code=500, detail="Failed to create post")

    return {"data": new_post}


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(id: int) -> None:
    post_index: int | None = search_index(id)
    if post_index is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The post with id: {id} wasn't found.")
    all_posts.pop(post_index)
    return


@app.put("/posts/{id}")
async def update_post(id: int, post: Post) -> dict[str, Any]:
    post_index: int | None = search_index(id)

    if post_index is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The post with id: {id} wasn't found.")
    
    updated_post: dict[str, Any] = post.model_dump()
    updated_post["id"] = id
    all_posts[post_index] = updated_post
    return {"data": updated_post}