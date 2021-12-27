from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql.functions import func
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import Boolean, DateTime, Integer, String

from app.db import Base


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True)
    content = Column(String(length=1024), nullable=False)
    displayed = Column(Boolean, default=False, nullable=False)

    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    conversation = relationship("Conversation", back_populates="messages")

    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    author = relationship("User", back_populates="messages")

    sent = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
