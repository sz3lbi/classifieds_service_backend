from pydantic import BaseModel, Field
from uuid import UUID


class ImageCreate(BaseModel):
    classified_id: int


class Image(ImageCreate):
    id: int
    filename: UUID
    extension: str = Field(max_length=8)

    class Config:
        orm_mode = True
