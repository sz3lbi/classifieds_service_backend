from pydantic import BaseModel
from uuid import UUID


class ImageCreate(BaseModel):
    classified_id: int


class Image(ImageCreate):
    id: int
    filename: UUID
    extension: str

    class Config:
        orm_mode = True
