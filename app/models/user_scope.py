from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import String
from sqlalchemy.dialects.postgresql import UUID

from app.db import Base


class UserScope(Base):
    __tablename__ = "users_scopes"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    user = relationship("User", back_populates="users_scopes")
    scope_name = Column(String(length=32), ForeignKey("scopes.name"), primary_key=True)
    scope = relationship("Scope", back_populates="users_scopes")
