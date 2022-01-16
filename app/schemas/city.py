from pydantic import BaseModel, Field


class CityCreate(BaseModel):
    name: str = Field(max_length=32)
    voivodeship_id: int


class CityUpdate(CityCreate):
    pass


class City(CityCreate):
    id: int

    class Config:
        orm_mode = True


class CityDelete(BaseModel):
    id: int

    class Config:
        orm_mode = True
