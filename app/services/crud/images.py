from abc import ABC
from typing import Sequence, Optional

from sqlalchemy import select

from app.db.tables import Image
from app.models.images import ImageIn
from app.services.crud.common import CRUD


class ImagesCRUD(CRUD, ABC):
    async def create(self, image_data: ImageIn) -> Image:
        image = Image(**image_data.model_dump())
        self.session.add(image)
        await self.session.commit()
        await self.session.refresh(image)

        return image

    async def read_all(self) -> Sequence[Image]:
        images = await self.session.scalars(select(Image))

        return images

    async def read_one(self, image_id: int) -> Optional[Image]:
        return await self.session.scalar(select(Image).where(Image.id == image_id).limit(1))

    async def update(self, image_id: str, image_data: ImageIn):
        image: Image = await self.read_one(image_id)
        image.update_entity(**image_data.model_dump())
        await self.session.commit()
        await self.session.refresh(image)

        return image

    async def delete(self, image_id: str) -> None:
        image: Image = self.read_one(image_id)
        await self.session.delete(image)
        await self.session.commit()
