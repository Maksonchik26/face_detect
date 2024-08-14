from typing import List

from pydantic import BaseModel

from app.db.tables import Person


class ImageIn(BaseModel):
    name: str
    persons: List[Person]
    bounding_box: dict
    gender: str
    age: int


class ImageOut(ImageIn):
    id: int
