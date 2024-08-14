from abc import ABC
from typing import Sequence, Optional

from sqlalchemy import select

from app.db.tables import Task
from app.models.tasks import TaskIn
from app.services.crud.common import CRUD


class PersonsCRUD(CRUD, ABC):
    async def create(self, task_data: TaskIn) -> Task:
        task = Task(**task_data.model_dump())
        self.session.add(task)
        await self.session.commit()
        await self.session.refresh(task)

        return task

    async def read_all(self) -> Sequence[Task]:
        return await self.session.scalars(select(Task))

    async def read_one(self, task_id: int) -> Optional[Task]:
        return await self.session.scalar(select(Task).where(Task.id == task_id).limit(1))

    async def update(self, task_id: str, task_data: TaskIn):
        task: Task = self.read_one(task_id)
        task.update_entity(**task_data.model_dump())
        await self.session.commit()
        await self.session.refresh(task)

        return task

    async def delete(self, task_id: str) -> None:
        task: Task = self.read_one(task_id)
        await self.session.delete(task)
        await self.session.commit()
