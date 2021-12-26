from uuid import UUID

from pydantic import BaseModel


class UserScopeCreate(BaseModel):
    user_id: UUID
    scope_name: str


class UserScope(UserScopeCreate):
    class Config:
        orm_mode = True
