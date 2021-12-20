from pydantic import BaseModel
from decimal import Decimal
from app.models.classified import ClassifiedStatus


class ClassifiedCreate(BaseModel):
    name: str
    title: str
    content: str
    price: Decimal
    status: ClassifiedStatus
    category_id: int
    city_id: int


class ClassifiedUpdate(ClassifiedCreate):
    pass


class Classified(ClassifiedCreate):
    id: int

    class Config:
        orm_mode = True
