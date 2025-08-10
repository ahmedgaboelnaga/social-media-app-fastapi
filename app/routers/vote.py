from typing import Annotated

from fastapi import HTTPException, status, APIRouter, Depends

from app.core import SessionDep, get_current_active_user
from app.models import User, Vote, Post
from app.schemas import VoteAction, VoteCreate, VoteResponse

router = APIRouter(prefix="/vote", tags=["Voting"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=VoteResponse)
async def vote(
    vote: VoteCreate,
    db: SessionDep,
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> VoteResponse:
    post_exists = db.query(Post).filter(Post.id == vote.post_id).first()
    if not post_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {vote.post_id} does not exist",
        )

    vote_query = db.query(Vote).filter_by(post_id=vote.post_id, user_id=current_user.id)
    found_vote = vote_query.first()
    if vote.action == VoteAction.UPVOTE:
        if found_vote and str(found_vote.type) == VoteAction.UPVOTE:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"User {current_user.id} already upvoted on post with id {vote.post_id}.",
            )
        if found_vote:
            vote_query.update(
                {"type": VoteAction.UPVOTE}, synchronize_session="evaluate"
            )
        else:
            new_vote: Vote = Vote(
                user_id=current_user.id, post_id=vote.post_id, type=VoteAction.UPVOTE
            )
            db.add(new_vote)
    elif vote.action == VoteAction.DOWNVOTE:
        if found_vote and str(found_vote.type) == VoteAction.DOWNVOTE:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"User {current_user.id} already down_voted on post with id {vote.post_id}.",
            )
        if found_vote:
            vote_query.update(
                {"type": VoteAction.DOWNVOTE}, synchronize_session="evaluate"
            )
        else:
            new_downvote: Vote = Vote(
                user_id=current_user.id, post_id=vote.post_id, type=VoteAction.DOWNVOTE
            )
            db.add(new_downvote)
    elif vote.action == VoteAction.REMOVE:
        if not found_vote:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Vote doesn't exist"
            )
        vote_query.delete(synchronize_session=False)

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    return VoteResponse(message=f"Vote {vote.action} successful")
