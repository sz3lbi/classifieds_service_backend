from uuid import UUID

from pydantic import BaseModel, Field


class UserScopeCreate(BaseModel):
    user_id: UUID
    scope_name: str = Field(max_length=32)


class UserScope(UserScopeCreate):
    class Config:
        orm_mode = True
