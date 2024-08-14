from abc import ABC
from typing import Sequence, Optional

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db.tables import Task, Image
from app.models.tasks import TaskIn
from app.services.crud.common import CRUD
from app.services.crud.images import ImagesCRUD


class TasksCRUD(CRUD, ABC):
    async def create(self, task_data: TaskIn) -> Task:
        task = Task(**task_data.model_dump())
        self.session.add(task)
        await self.session.commit()
        await self.session.refresh(task)

        return task

    async def read_all(self, images_crud: ImagesCRUD = Depends()) -> Sequence[Task]:
        # stmt = select(Task).options(
        #     selectinload(Task.images).selectinload(Image.persons)
        # )
        #
        # # Выполняем запрос
        # result = self.session.execute(stmt)
        #
        # # Извлекаем все задачи из результата
        # tasks = result.scalars().all()

        return await self.session.scalar(select(Task).options(selectinload(Task.images).selectinload(Image.persons)))

    async def read_one(self, task_id: int) -> Optional[Task]:
        return await self.session.scalar(select(Task).options(selectinload(Task.images).selectinload(Image.persons)).where(Task.id == task_id).limit(1))

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
