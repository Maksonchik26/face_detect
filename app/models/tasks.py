from typing import List

from pydantic import BaseModel


class TaskIn(BaseModel):
    name: str


class TaskOut(TaskIn):
    id: int
    status: str
    images: List[ImageOut]
