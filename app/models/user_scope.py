from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import Column, ForeignKey, UniqueConstraint
from sqlalchemy.sql.sqltypes import Integer, String
from sqlalchemy.dialects.postgresql import UUID

from app.db import Base


class UserScope(Base):
    __tablename__ = "users_scopes"

    id = Column(Integer, primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="users_scopes")
    scope_name = Column(
        String(length=32), ForeignKey("scopes.scope_name"), nullable=False
    )
    scope = relationship("Scope", back_populates="users_scopes")

    __table_args__ = (UniqueConstraint(user_id, scope_name),)
