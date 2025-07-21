from datetime import datetime
from pydantic import BaseModel

class PostCreate(BaseModel):
    title: str
    content: str
    published: bool = True
    # rating: Optional[int] = None # This helps us to give it None if we don't have an integer instead of passing a default int like zero or True for bool
    # rating: int | None = None
    rating: int | None = None


class PostResponse(PostCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True