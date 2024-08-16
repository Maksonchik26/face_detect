from typing import List, Optional

from pydantic import BaseModel

from app.models.images import ImageOut


class TaskIn(BaseModel):
    name: str


class TaskOut(TaskIn):
    id: int
    total_persons: Optional[int]
    total_males: Optional[int]
    total_females: Optional[int]
    average_female_age: Optional[float]
    average_male_age: Optional[float]
    status: str
    images: List[ImageOut]


class TaskCount(BaseModel):
    total_persons: Optional[int]
    total_males: Optional[int]
    total_females: Optional[int]
    average_male_age: Optional[float]
    average_female_age: Optional[float]
