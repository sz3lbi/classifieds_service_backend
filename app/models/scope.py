from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import String

from app.db import Base


class Scope(Base):
    __tablename__ = "scopes"

    name = Column(String(length=32), primary_key=True)
    description = Column(String(length=128), nullable=False)

    users_scopes = relationship(
        "UserScope", back_populates="scope", cascade="all, delete"
    )
