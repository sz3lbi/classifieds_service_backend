from decimal import Decimal

from pydantic import BaseModel, Field

from app.models.classified import ClassifiedStatus


class ClassifiedCreate(BaseModel):
    title: str = Field(max_length=32)
    content: str = Field(max_length=8192)
    price: Decimal
    status: ClassifiedStatus
    category_id: int
    city_id: int


class ClassifiedUpdate(ClassifiedCreate):
    pass


class Classified(ClassifiedCreate):
    id: int
    user_id: int

    class Config:
        orm_mode = True
