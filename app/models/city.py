from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import Integer, String

from app.db import Base


class City(Base):
    __tablename__ = "cities"

    id = Column(Integer, primary_key=True)
    voivodeship_id = Column(Integer, ForeignKey("voivodeships.id"), nullable=False)
    voivodeship = relationship("Voivodeship", back_populates="cities")
    name = Column(String(length=32), nullable=False)

    classifieds = relationship(
        "Classified", back_populates="city", cascade="all, delete"
    )
