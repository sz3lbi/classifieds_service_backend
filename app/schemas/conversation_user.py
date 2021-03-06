from uuid import UUID

from pydantic import BaseModel


class ConversationUserCreate(BaseModel):
    conversation_id: int
    user_id: UUID


class ConversationUser(ConversationUserCreate):
    id: int

    class Config:
        orm_mode = True


class ConversationUserDelete(BaseModel):
    id: int

    class Config:
        orm_mode = True
