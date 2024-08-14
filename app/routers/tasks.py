from typing import List

from fastapi import APIRouter, Depends, Response, status

from app.models.tasks import TaskOut, TaskIn
from app.services.crud.tasks import TasksCRUD

router = APIRouter(prefix="/tasks", tags=["task"])


@router.get("/", response_model=TaskOut, status_code=status.HTTP_200_OK)
async def tasks_get_all(tasks_crud: TasksCRUD = Depends()):
    tasks = await tasks_crud.read_all()

    return tasks


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_task(
        task_data: TaskIn,
        task_crud: TasksCRUD = Depends()
):
    task = await task_crud.create(task_data)

    return task

