from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from uuid import UUID


class User(BaseModel):
    id: UUID
    email: EmailStr = Field(max_length=320)
    is_active: bool = True
    is_superuser: bool = False

    class Config:
        orm_mode = True


class UserCreate(BaseModel):
    email: EmailStr = Field(max_length=320)
    password: str = Field(max_length=71)  # 1 byte null terminator


class UserUpdate(UserCreate):
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False


class UserDB(User):
    hashed_password: str = Field(max_length=72)
