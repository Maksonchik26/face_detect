from typing import List

from pydantic import BaseModel

from app.models.persons import PersonOut


class ImageIn(BaseModel):
    name: str
    persons: List[PersonOut]


class ImageOut(ImageIn):
    id: int
    # task_id: int
