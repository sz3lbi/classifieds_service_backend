from fastapi_users_db_sqlalchemy import GUID
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import Integer, String

from app.db import Base


class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True)
    filename = Column(UUID(as_uuid=True), unique=True)
    extension = Column(String(length=8))
    user_id = Column(GUID, ForeignKey("users.id"))
    user = relationship("User", back_populates="images")

    classifieds = relationship(
        "Classified", back_populates="image", cascade="all, delete"
    )
