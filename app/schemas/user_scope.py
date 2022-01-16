from uuid import UUID

from pydantic import BaseModel, Field

from app.db import Base


class UserScopeCreate(BaseModel):
    user_id: UUID
    scope_name: str = Field(max_length=32)


class UserScope(UserScopeCreate):
    id: int

    class Config:
        orm_mode = True


class UserScopeDelete(BaseModel):
    id: int

    class Config:
        orm_mode = True
