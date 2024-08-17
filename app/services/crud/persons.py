from abc import ABC
from typing import Sequence, Optional

from sqlalchemy import select

from app.db.tables import Person
from app.models.persons import PersonIn
from app.services.crud.common import CRUD


class PersonsCRUD(CRUD, ABC):
    async def create(self, person_data: PersonIn) -> Person:
        person = Person(**person_data.model_dump())
        self.session.add(person)
        await self.session.commit()
        await self.session.refresh(person)
        person = await self.read_one(person.id)

        return person

    async def read_all(self) -> Sequence[Person]:
        return await self.session.scalars(select(Person))

    async def read_one(self, person_id: int) -> Optional[Person]:
        return await self.session.scalar(select(Person).where(Person.id == person_id).limit(1))

    async def update(self, person_id: str, person_data: PersonIn):
        person: Person = self.read_one(person_id)
        person.update_entity(**person_data.model_dump())
        await self.session.commit()
        await self.session.refresh(person)
        person = await self.read_one(person.id)

        return person

    async def delete(self, person_id: str) -> None:
        person: Person = self.read_one(person_id)
        await self.session.delete(person)
        await self.session.commit()
