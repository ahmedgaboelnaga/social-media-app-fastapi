from sqlalchemy import TIMESTAMP, Column, Integer, String, text
from sqlalchemy.orm import relationship

from app.core import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )

    posts = relationship("Post", back_populates="owner")
