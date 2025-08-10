from pydantic import BaseModel
from enum import Enum


class VoteAction(str, Enum):
    UPVOTE = "upvote"
    DOWNVOTE = "downvote"
    REMOVE = "remove"


class VoteCreate(BaseModel):
    post_id: int
    action: VoteAction


class VoteResponse(BaseModel):
    message: str
