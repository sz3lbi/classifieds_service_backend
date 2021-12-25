from app.db import Base
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import Integer, String


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)
    name = Column(String(length=32), nullable=False, unique=True)
    description = Column(String(length=128))

    classifieds = relationship(
        "Classified", back_populates="category", cascade="all, delete"
    )
