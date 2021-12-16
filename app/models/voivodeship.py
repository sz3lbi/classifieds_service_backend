from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import Integer, String

from app.db import Base


class Voivodeship(Base):
    __tablename__ = "voivodeships"

    id = Column(Integer, primary_key=True)
    name = Column(String(length=32))
    cities = relationship("City", back_populates="voivodeship", cascade="all, delete")
