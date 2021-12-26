from pydantic import BaseModel, Field


class CategoryCreate(BaseModel):
    name: str = Field(max_length=32)
    description: str = Field(max_length=128)


class CategoryUpdate(CategoryCreate):
    pass


class Category(CategoryCreate):
    id: int

    class Config:
        orm_mode = True
