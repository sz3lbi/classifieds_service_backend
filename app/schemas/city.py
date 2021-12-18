from pydantic import BaseModel


class CityCreate(BaseModel):
    name: str
    voivodeship_id: int


class CityUpdate(CityCreate):
    pass


class City(CityCreate):
    id: int

    class Config:
        orm_mode = True
