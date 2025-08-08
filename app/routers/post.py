from typing import Annotated, List

from fastapi import HTTPException, status, APIRouter, Depends
from sqlalchemy import desc

from app.core import SessionDep, get_current_active_user
from app.models import User, Post
from app.schemas import PostCreate, PostResponse


router = APIRouter(prefix="/posts", tags=["Posts"])


@router.get("", response_model=List[PostResponse])
async def get_posts(
    db: SessionDep,
    current_user: Annotated[User, Depends(get_current_active_user)],
    limit: int = 10,
    skip: int = 0,
    search: str | None = "",
) -> List[Post]:
    posts: List[Post] = (
        db.query(Post)
        .filter(Post.title.contains(search))
        .limit(limit)
        .offset(skip)
        .all()
    )
    return posts


@router.get("/me", response_model=List[PostResponse])
async def get_my_posts(
    db: SessionDep,
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> List[Post]:
    return current_user.posts


@router.get("/latest", response_model=PostResponse)
async def get_latest_post(
    db: SessionDep,
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Post:
    post_query = db.query(Post).order_by(desc(Post.created_at))
    post: Post | None = post_query.first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="There are no posts yet."
        )
    return post


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(
    post_id: int,
    db: SessionDep,
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Post:
    post: Post | None = db.query(Post).filter_by(id=post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id: {post_id} was not found",
        )
    return post


@router.post("", status_code=status.HTTP_201_CREATED, response_model=PostResponse)
async def create_post(
    post: PostCreate,
    db: SessionDep,
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Post:
    new_post: Post = Post(**post.model_dump(), owner_id=current_user.id)
    try:
        db.add(new_post)
        db.commit()
        db.refresh(new_post)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    return new_post


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: int,
    db: SessionDep,
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> None:
    post_query = db.query(Post).filter_by(id=post_id)
    post: Post | None = post_query.first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"The post with id: {post_id} wasn't found.",
        )
    if post.owner_id != current_user.id:  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this post",
        )
    post_query.delete(synchronize_session=False)
    db.commit()
    return


@router.put("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: int,
    updated_post: PostCreate,
    db: SessionDep,
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Post:
    post_query = db.query(Post).filter_by(id=post_id)
    post: Post | None = post_query.first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"The post with id: {post_id} wasn't found.",
        )
    if post.owner_id != current_user.id:  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this post",
        )
    # try:
    #     post_query.update(updated_post.model_dump(), synchronize_session=False)
    #     db.commit()
    #     db.refresh(post)
    try:
        for key, value in updated_post.model_dump().items():
            setattr(post, key, value)
        # post_query.update(post, synchronize_session=False)
        db.commit()
        db.refresh(post)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Databaase Error {e}",
        )
    return post
