from pydantic import BaseModel


class PersonIn(BaseModel):
    bounding_box: dict
    age: int
    gender: str


class PersonOut(PersonIn):
    id: int
    image_id: int
