from fastapi import HTTPException, status, APIRouter, Depends
from typing import Annotated

from app.core import SessionDep, get_current_active_user
from app.utils import hash_password
from app.models import User
from app.schemas import UserCreate, UserResponse


router = APIRouter(prefix="/users", tags=["Users"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
async def create_user(user: UserCreate, db: SessionDep) -> User:
    user_data = user.model_dump()
    user_data["password"] = hash_password(user_data["password"])
    new_user = User(**user_data)
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


@router.get("/me", response_model=UserResponse)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> User:
    return current_user


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: SessionDep) -> User:
    user: User | None = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id: {user_id} not found!",
        )
    return user
