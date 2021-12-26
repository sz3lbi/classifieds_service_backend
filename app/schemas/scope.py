from pydantic import BaseModel


class ScopeCreate(BaseModel):
    name: str
    description: str


class ScopeUpdate(BaseModel):
    description: str


class Scope(ScopeCreate):
    class Config:
        orm_mode = True
