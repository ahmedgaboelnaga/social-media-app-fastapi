from datetime import datetime
from pydantic import BaseModel, ConfigDict

from .user import UserResponse


class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    # rating: Optional[int] = None # This helps us to give it None if we don't have an integer instead of passing a default int like zero or True for bool
    # rating: int | None = None
    rating: int | None = None


class PostCreate(Post):
    pass


class PostResponse(Post):
    id: int
    created_at: datetime
    owner_id: int
    owner: UserResponse

    model_config = ConfigDict(from_attributes=True)
