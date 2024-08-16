from typing import List

from pydantic import BaseModel

from app.models.persons import PersonOut


class ImageIn(BaseModel):
    name: str


class ImageOut(ImageIn):
    id: int
    persons: List[PersonOut]
