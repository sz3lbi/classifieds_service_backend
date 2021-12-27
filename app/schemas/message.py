from uuid import UUID

from pydantic import BaseModel, Field


class MessageCreate(BaseModel):
    conversation_id: int
    content: str = Field(max_length=1024)
    displayed: bool = Field(default=False)


class MessageUpdate(BaseModel):
    displayed: bool


class Message(MessageCreate):
    id: int
    author_id: UUID

    class Config:
        orm_mode = True
