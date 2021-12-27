from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import Integer, String

from app.db import Base


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True)
    subject = Column(String(length=64), nullable=False)

    messages = relationship(
        "Message", back_populates="conversation", cascade="all, delete"
    )
    conversations_users = relationship(
        "ConversationUser", back_populates="conversation", cascade="all, delete"
    )
