from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import Integer, String

from app.db import Base


class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True)
    filename = Column(UUID(as_uuid=True), nullable=False, unique=True)
    extension = Column(String(length=8), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="images")

    classified_id = Column(Integer, ForeignKey("classifieds.id"), nullable=False)
    classified = relationship(
        "Classified", back_populates="images", cascade="all, delete"
    )
