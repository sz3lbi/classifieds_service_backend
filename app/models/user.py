from fastapi_users.db import SQLAlchemyBaseUserTable
from sqlalchemy import Column, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql.functions import func

from app.db import Base


class User(Base, SQLAlchemyBaseUserTable):
    __tablename__ = "users"

    created = Column(DateTime(timezone=True), server_default=func.now())
    updated = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    classifieds = relationship(
        "Classified", back_populates="user", cascade="all, delete"
    )
    images = relationship("Image", back_populates="user", cascade="all, delete")

    def __repr__(self):
        return f"User(id={repr(self.id)}, name={repr(self.email)})"
