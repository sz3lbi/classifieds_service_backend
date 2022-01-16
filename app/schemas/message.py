from uuid import UUID

from pydantic import BaseModel, Field


class MessageCreate(BaseModel):
    conversation_id: int
    content: str = Field(max_length=1024)


class MessageUpdate(BaseModel):
    displayed: bool


class Message(MessageCreate):
    id: int
    author_id: UUID
    displayed: bool = Field(default=False)

    class Config:
        orm_mode = True


class MessageDelete(BaseModel):
    id: int

    class Config:
        orm_mode = True
