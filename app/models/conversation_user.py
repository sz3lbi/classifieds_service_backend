from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import Column, ForeignKey, UniqueConstraint
from sqlalchemy.sql.sqltypes import Integer
from sqlalchemy.dialects.postgresql import UUID

from app.db import Base


class ConversationUser(Base):
    __tablename__ = "conversations_users"

    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    conversation = relationship("Conversation", back_populates="conversations_users")
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="conversations_users")

    __table_args__ = (UniqueConstraint(conversation_id, user_id),)
