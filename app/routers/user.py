from fastapi import HTTPException, status, APIRouter, Depends
from typing import Annotated
from .. import schemas, models, utils
from ..database import DBSession
from ..oauth2 import get_current_active_user


router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "", status_code=status.HTTP_201_CREATED, response_model=schemas.UserResponse
)
async def create_user(user: schemas.UserCreate, db: DBSession) -> models.User:
    user.password = utils.hash_password(user.password)
    new_user: models.User = models.User(**user.model_dump())
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database Error! {str(e)}",
        )
    return new_user


@router.get("/me", response_model=schemas.UserResponse)
async def read_users_me(
    current_user: Annotated[models.User, Depends(get_current_active_user)],
) -> models.User:
    return current_user


@router.get("/{user_id}", response_model=schemas.UserResponse)
async def get_user(user_id: int, db: DBSession) -> models.User:
    user: models.User | None = (
        db.query(models.User).filter(models.User.id == user_id).first()
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id: {user_id} not found!",
        )
    return user
