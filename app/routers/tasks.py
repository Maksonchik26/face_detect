import os
from typing import List

from fastapi import APIRouter, Depends, status, UploadFile, File, HTTPException

from app.models.persons import PersonIn
from app.models.tasks import TaskOut, TaskIn, TaskCount
from app.services.crud.images import ImagesCRUD
from app.services.crud.persons import PersonsCRUD
from app.services.crud.tasks import TasksCRUD
from app.services.system.facecloud import detect_faces_api
from app.services.system.task_funcs import count_total_persons_and_age_by_gender, count_average_age

router = APIRouter(prefix="/tasks", tags=["task"])


@router.get("/", response_model=List[TaskOut], status_code=status.HTTP_200_OK)
async def tasks_get_all(tasks_crud: TasksCRUD = Depends()):
    tasks = await tasks_crud.read_all()

    return tasks


@router.get("/{task_id}", response_model=TaskOut, status_code=status.HTTP_200_OK)
async def tasks_get_all(task_id: int, tasks_crud: TasksCRUD = Depends()):
    task = await tasks_crud.read_one(task_id)

    return task


@router.post("/", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
async def create_task(
        task_data: TaskIn,
        task_crud: TasksCRUD = Depends()
):
    task = await task_crud.create(task_data)

    return task


@router.put("/{task_id}/add_image", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
async def add_image_to_task(
        task_id: int,
        file: UploadFile = File(...),
        images_crud: ImagesCRUD = Depends(),
        task_crud: TasksCRUD = Depends(),
        persons_crud: PersonsCRUD = Depends(),
):
    # Create directory and save file
    directory = "images"
    file_location = os.path.join(directory, file.filename)
    os.makedirs(directory, exist_ok=True)

    task = await task_crud.read_one(task_id)
    image_names_in_task = [image.name for image in task.images]

    # Check if image with same name already exist
    if file.filename in image_names_in_task:
        raise HTTPException(status_code=400, detail="Image with the same name already exists in the Task")

    # Create image in DB and save into the task
    image = await images_crud.create(task_id, file.filename)
    await task_crud.add_image_to_task(task_id, image.id)

    # Image processing and person detection
    image_persons_data = await detect_faces_api(file)

    # TODO Подумать над выносом всей логики расчета отсюда
    # Get statistic from the image
    total_males_and_age_image = count_total_persons_and_age_by_gender(image_persons_data, "male")
    total_females_and_age_image = count_total_persons_and_age_by_gender(image_persons_data, "female")

    # Counting new statistic for task
    total_persons = total_females_and_age_image["persons"] + total_males_and_age_image["persons"] + (task.total_persons or 0)
    total_males = total_males_and_age_image["persons"] + (task.total_males or 0)
    total_females = total_females_and_age_image["persons"] + (task.total_females or 0)

    avg_male_age_task = count_average_age(
        total_males_and_age_image["age"] + (task.total_males * task.average_male_age if task.total_males and task.average_male_age else 0),
        total_males
    ) if total_males > 0 else 0

    avg_female_age_task = count_average_age(
        total_females_and_age_image["age"] + (task.total_females * task.average_female_age if task.total_females and task.average_female_age else 0),
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
            image_id=image.id
        )

        person = await persons_crud.create(person_data)
        persons_list.append(person)

    # Bind persons to the image
    image.persons.extend(persons_list)
    await images_crud.session.commit()
    await images_crud.session.refresh(image)

    # Save image on disk
    try:
        with open(file_location, "wb") as buffer:
            buffer.write(await file.read())
    except IOError as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    # Update task
    await task_crud.update(task_id, task_data)

    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
        task_id: int,
        tasks_crud: TasksCRUD = Depends()
):
    await tasks_crud.delete(task_id)


# @router.put("/{task_id}/sync_demographic_data", response_model=TaskOut, status_code=status.HTTP_200_OK)
# async def sync_demographic_data(
#         task_id: int,
#         images_crud: ImagesCRUD = Depends(),
#         task_crud: TasksCRUD = Depends()
# ):
    # task = await task_crud.read_one(task_id)
    #
    #
    # for image in task.images:

    pass
    # TODO Синхронизацию данных (если имеджи будут удаляться из базы лучше сделать с итерацией по имеджам, но в них должны быть поля с возрастом и количеством людей)

