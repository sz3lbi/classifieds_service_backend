from pydantic import BaseModel, Field


class ConversationCreate(BaseModel):
    subject: str = Field(max_length=64)


class Conversation(ConversationCreate):
    id: int

    class Config:
        orm_mode = True
