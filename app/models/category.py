from app.db import Base
from fastapi_users_db_sqlalchemy import GUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import null
from sqlalchemy.sql.functions import func
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import VARCHAR, DateTime, Integer, String


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)
    name = Column(String(length=32))
    description = Column(String(length=128))

    classifieds = relationship("Classified", back_populates="category", cascade="all, delete")
