from pydantic import BaseModel


class VoivodeshipCreate(BaseModel):
    name: str


class VoivodeshipUpdate(VoivodeshipCreate):
    pass


class Voivodeship(VoivodeshipCreate):
    id: int

    class Config:
        orm_mode = True
