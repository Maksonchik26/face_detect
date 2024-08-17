from abc import ABC
from typing import Sequence, Optional

from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import selectinload, joinedload

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
        task = await self.read_one(task.id)

        return task

    async def read_all(self, images_crud: ImagesCRUD = Depends()) -> Sequence[Task]:
        tasks = await self.session.execute(select(Task).options(selectinload(Task.images).
                                                                selectinload(Image.persons)))
        tasks = tasks.scalars().all()

        return tasks

    async def read_one(self, task_id: int) -> Task:
        return await self.session.scalar(
            select(Task).options(
                selectinload(Task.images).selectinload(Image.persons)
            ).where(Task.id == task_id).limit(1)
        )

    async def update(self, task_id: str, task_data: TaskIn):
        task: Task = await self.read_one(task_id)
        task.update_entity(**task_data.model_dump())
        await self.session.commit()
        await self.session.refresh(task)
        task = await self.read_one(task.id)

        return task

    async def add_image_to_task(self, task_id: int, image_id: int):
        task = await self.read_one(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        # Assuming `task.images` is a relationship and you can append images
        image = await self.session.get(Image, image_id)
        if not image:
            raise HTTPException(status_code=404, detail="Image not found")

        task.images.append(image)
        await self.session.commit()
        await self.session.refresh(task)
        task = await self.read_one(task.id)

        return task

    async def delete(self, task_id: str) -> None:
        task: Task = await self.read_one(task_id)
        await self.session.delete(task)
        await self.session.commit()
