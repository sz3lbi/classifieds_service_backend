from uuid import uuid4

from sqlalchemy import Column, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql.functions import func
from sqlalchemy.sql.sqltypes import Boolean, String
from sqlalchemy.dialects.postgresql import UUID

from app.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    email = Column(String(length=320), unique=True, index=True, nullable=False)
    hashed_password = Column(String(length=72), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)

    created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    classifieds = relationship(
        "Classified", back_populates="user", cascade="all, delete"
    )
    images = relationship("Image", back_populates="user", cascade="all, delete")
    users_scopes = relationship(
        "UserScope", back_populates="user", cascade="all, delete"
    )

    def __repr__(self):
        return f"User(id={repr(self.id)}, name={repr(self.email)})"
