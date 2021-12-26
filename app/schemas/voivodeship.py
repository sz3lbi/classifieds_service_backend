from pydantic import BaseModel, Field


class VoivodeshipCreate(BaseModel):
    name: str = Field(max_length=32)


class VoivodeshipUpdate(VoivodeshipCreate):
    pass


class Voivodeship(VoivodeshipCreate):
    id: int

    class Config:
        orm_mode = True
