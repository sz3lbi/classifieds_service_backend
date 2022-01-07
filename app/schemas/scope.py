from typing import Optional
from pydantic import BaseModel, Field


class ScopeCreate(BaseModel):
    scope_name: str = Field(max_length=32)
    description: str = Field(max_length=128)
    default: Optional[bool] = Field(default=False)


class ScopeUpdate(BaseModel):
    description: str = Field(max_length=128)


class Scope(ScopeCreate):
    class Config:
        orm_mode = True
