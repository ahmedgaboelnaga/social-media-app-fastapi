from typing import Annotated

from fastapi import Depends
from sqlalchemy import create_engine

# from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session

from .config import settings


# Base = declarative_base()
class Base(DeclarativeBase):
    pass


SQLALCHEMY_DATABASE_URL = settings.database_url

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_tables():
    Base.metadata.create_all(bind=engine)


def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


SessionDep = Annotated[Session, Depends(get_db)]
