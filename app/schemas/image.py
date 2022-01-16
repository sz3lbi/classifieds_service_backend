from pydantic import BaseModel, Field
from uuid import UUID


class Image(BaseModel):
    id: int
    classified_id: int

    class Config:
        orm_mode = True


class ImageCreate(BaseModel):
    classified_id: int


class ImageDB(Image):
    id: int
    filename: UUID
    extension: str = Field(max_length=8)


class ImageDelete(BaseModel):
    id: int
