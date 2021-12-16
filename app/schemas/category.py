from pydantic import BaseModel


class CategoryCreate(BaseModel):
    name: str
    description: str


class CategoryUpdate(CategoryCreate):
    pass


class Category(CategoryCreate):
    id: int

    class Config:
        orm_mode = True
