from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import Integer, String
from sqlalchemy.dialects.postgresql import UUID

from app.db import Base


class ConversationUser(Base):
    __tablename__ = "conversations_users"

    conversation_id = Column(Integer, ForeignKey("conversations.id"), primary_key=True)
    conversation = relationship("Conversation", back_populates="conversations_users")
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    user = relationship("User", back_populates="conversations_users")
