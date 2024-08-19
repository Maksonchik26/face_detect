import os
from typing import List, Annotated

from fastapi import APIRouter, Depends, status, UploadFile, File, HTTPException, BackgroundTasks

from app.db.tables import Task, Image
from app.models.persons import PersonIn
from app.models.tasks import TaskOut, TaskIn, TaskCount, TaskStatus
from app.services.auth import verify_credentials
from app.services.crud.images import ImagesCRUD
from app.services.crud.persons import PersonsCRUD
from app.services.crud.tasks import TasksCRUD
from app.services.system.facecloud import detect_faces_api
from app.services.system.task_funcs import count_total_persons_and_age_by_gender, count_average_age

router = APIRouter(prefix="/tasks", tags=["task"])


@router.get("/", response_model=List[TaskOut], status_code=status.HTTP_200_OK)
async def tasks_get_all(
        credentials: Annotated[str, Depends(verify_credentials)],
        tasks_crud: TasksCRUD = Depends(),
):
    tasks = await tasks_crud.read_all()

    return tasks


@router.get("/{task_id}", response_model=TaskOut, status_code=status.HTTP_200_OK)
async def tasks_get_one(
        credentials: Annotated[str, Depends(verify_credentials)],
        task_id: int, tasks_crud: TasksCRUD = Depends()
):
    task = await tasks_crud.read_one(task_id)

    return task


@router.post("/", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
async def create_task(
        credentials: Annotated[str, Depends(verify_credentials)],
        task_data: TaskIn,
        task_crud: TasksCRUD = Depends()
):
    task = await task_crud.create(task_data)

    return task


@router.put("/{task_id}/add_image", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
async def add_image_to_task(
        credentials: Annotated[str, Depends(verify_credentials)],
        task_id: int,
        background_tasks: BackgroundTasks,
        file: UploadFile = File(...),
        images_crud: ImagesCRUD = Depends(),
        task_crud: TasksCRUD = Depends(),
        persons_crud: PersonsCRUD = Depends(),
):
    task = await task_crud.read_one(task_id)

    image_names_in_task = [image.name for image in task.images]

    # Check if image with same name already exist
    if file.filename in image_names_in_task:
        raise HTTPException(status_code=400, detail="Image with the same name already exists in the Task")

    image = await images_crud.create(task_id, file.filename)
    await task_crud.add_image_to_task(task_id, image.id)

    task.status = "in_progress"
    await task_crud.session.commit()

    file_bytes = await file.read()
    file_name = file.filename

    # Add image and start background task
    background_tasks.add_task(
        process_image_task,
        task,
        image,
        task_crud,
        persons_crud,
        images_crud,
        file_bytes,
        file_name
    )

    return task


async def process_image_task(
        task: Task,
        image: Image,
        task_crud: TasksCRUD,
        persons_crud: PersonsCRUD,
        images_crud: ImagesCRUD,
        file_bytes: bytes,
        file_name: str
):
    try:
        images_crud.session.add(image)
        await images_crud.session.commit()
        # Sending request to process image
        image_persons_data = await detect_faces_api(file_bytes)

        # Get statistic from the image
        total_males_and_age_image = count_total_persons_and_age_by_gender(image_persons_data, "male")
        total_females_and_age_image = count_total_persons_and_age_by_gender(image_persons_data, "female")

        # Counting new statistic for task
        total_persons = (total_females_and_age_image["persons"] + total_males_and_age_image["persons"] +
                         (task.total_persons or 0))
        total_males = total_males_and_age_image["persons"] + (task.total_males or 0)
        total_females = total_females_and_age_image["persons"] + (task.total_females or 0)

        avg_male_age_task = count_average_age(
            total_males_and_age_image["age"] +
            (task.total_males * task.average_male_age if task.total_males and task.average_male_age else 0),
            total_males
        ) if total_males > 0 else 0

        avg_female_age_task = count_average_age(
            total_females_and_age_image["age"] +
            (task.total_females * task.average_female_age if task.total_females and task.average_female_age else 0),
            total_females
        ) if total_females > 0 else 0

        task_data = TaskCount(
            total_persons=total_persons,
            total_males=total_males,
            total_females=total_females,
            average_male_age=avg_male_age_task,
            average_female_age=avg_female_age_task,
        )

        # Add persons to DB
        persons_list = []
        for person in image_persons_data["data"]:
            person_data = PersonIn(
                bounding_box=person["bbox"],
                age=int(person['demographics']['age']['mean']),
                gender=person['demographics']['gender'],
                image_id=image.id,
                pes=1
            )

            person = await persons_crud.create(person_data)
            persons_list.append(person)

        # Bind persons to the image
        image.persons.extend(persons_list)
        await images_crud.session.commit()
        await images_crud.session.refresh(image)

        # Save image on disk
        directory = "images"
        file_location = os.path.join(directory, file_name)
        os.makedirs(directory, exist_ok=True)

        with open(file_location, "wb") as buffer:
            buffer.write(file_bytes)

        await task_crud.update(task.id, task_data)
        task_status = TaskStatus(status="success")
        # Update task, set "success" status if everything is OK
        await task_crud.update(task.id, task_status)

    except Exception:
        # if error happened, set status "error"
        if image is not None:
            await images_crud.delete(image.id)
        if os.path.exists(f"{directory}/{file_name}"):
            os.remove(f"{directory}/{file_name}")
        task_status = TaskStatus(status="error")
        await task_crud.update(task.id, task_status)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
        task_id: int,
        tasks_crud: TasksCRUD = Depends()
):
    await tasks_crud.delete(task_id)
