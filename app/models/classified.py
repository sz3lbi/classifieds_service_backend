import enum

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql.functions import func
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import DateTime, Enum, Integer, Numeric, String

from app.db import Base


class ClassifiedStatus(int, enum.Enum):
    active = enum.auto()
    hidden = enum.auto()


class Classified(Base):
    __tablename__ = "classifieds"

    id = Column(Integer, primary_key=True)

    created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    title = Column(String(length=32), nullable=False)
    content = Column(String(length=8192), nullable=False)
    price = Column(Numeric(16, 2), nullable=False)
    status = Column(Enum(ClassifiedStatus), nullable=False)

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="classifieds")

    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    category = relationship("Category", back_populates="classifieds")

    city_id = Column(Integer, ForeignKey("cities.id"), nullable=False)
    city = relationship("City", back_populates="classifieds")

    images = relationship("Image", back_populates="classified", cascade="all, delete")
