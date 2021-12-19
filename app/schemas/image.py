from pydantic import BaseModel


class ImageCreate(BaseModel):
    filename: str
    extension: str


class Image(ImageCreate):
    id: int

    class Config:
        orm_mode = True
