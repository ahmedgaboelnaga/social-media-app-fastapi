from passlib.context import CryptContext
from . import models
from sqlalchemy.orm import Session

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_user(db: Session, username: str) -> models.User | None:
    user: models.User | None = db.query(models.User).filter_by(email=username).first()
    if not user:
        return None
    return user


def authenticate_user(db: Session, username: str, password: str) -> models.User | None:
    user: models.User | None = get_user(db, username)
    if not user or not verify_password(password, str(user.password)):
        return None
    return user
