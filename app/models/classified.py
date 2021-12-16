import enum

from fastapi_users_db_sqlalchemy import GUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql.functions import func
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import DateTime, Enum, Integer, Numeric, String

from app.db import Base

class ClassifiedStatus(enum.Enum):
    active = enum.auto()
    hidden = enum.auto()

class Classified(Base):
    __tablename__ = "classifieds"

    id = Column(Integer, primary_key=True)

    created = Column(DateTime(timezone=True), server_default=func.now())
    updated = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    
    title = Column(String(length=32))
    content = Column(String(length=8192))    
    price = Column(Numeric(16, 2))    
    status = Column(Enum(ClassifiedStatus))    

    user_id = Column(GUID, ForeignKey("users.id"))
    user = relationship("User", back_populates="classifieds")

    category_id = Column(Integer, ForeignKey("categories.id"))
    category = relationship("Category", back_populates="classifieds")

    city_id = Column(Integer, ForeignKey("cities.id"))
    city = relationship("City", back_populates="classifieds")

    images = relationship("Image", back_populates="classified", cascade="all, delete")
