from datetime import datetime
from pydantic import BaseModel, ConfigDict

from .user import UserResponse


class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True
    # rating: Optional[int] = None # This helps us to give it None if we don't have an integer instead of passing a default int like zero or True for bool
    # rating: int | None = None
    rating: int | None = None


class PostCreate(PostBase):
    pass


class PostResponse(PostBase):
    id: int
    created_at: datetime
    owner_id: int
    owner: UserResponse

    model_config = ConfigDict(from_attributes=True)


class PostWithVote(BaseModel):
    Post: PostResponse
    votes: int

    model_config = ConfigDict(from_attributes=True)
