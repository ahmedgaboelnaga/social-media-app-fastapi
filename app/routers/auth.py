from datetime import timedelta
from typing import Annotated
from fastapi import HTTPException, status, APIRouter, Depends
from .. import models, utils, schemas, oauth2
from ..database import DBSession
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(tags=["Authentication"])


@router.post("/auth", response_model=schemas.Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: DBSession
) -> schemas.Token:
    user: models.User | None = utils.authenticate_user(
        db, form_data.username, form_data.password
    )
    if not user:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=oauth2.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = oauth2.create_access_token(
        data={"sub": str(user.email)}, expires_delta=access_token_expires
    )
    return schemas.Token(access_token=access_token, token_type="bearer")
