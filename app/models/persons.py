from pydantic import BaseModel


class PersonIn(BaseModel):
    bounding_box: dict
    age: int
    gender: str
    image_id: int


class PersonOut(PersonIn):
    id: int
