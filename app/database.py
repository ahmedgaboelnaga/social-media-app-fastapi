from typing import Annotated
from fastapi import Depends
from sqlalchemy import create_engine
# from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session
# from sqlalchemy import declarative_base  # This is another way to get the declarative base but to define it as an instance not as a class


# Base = declarative_base()
class Base(DeclarativeBase):
    pass

# SQLALCHEMY_DATABASE_URL = 'postgresql://<username>:<password>@<ip-address/hostname>:<port>/<database_name>'
SQLALCHEMY_DATABASE_URL = 'postgresql+psycopg://postgres:645798@localhost:5432/fastapi'

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()

DBSession = Annotated[Session, Depends(get_db)]
