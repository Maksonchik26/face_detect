import asyncio


from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.db.tables import BaseModel

#TODO Убрать URL в .env
engine = create_async_engine(url="postgresql+asyncpg://admin:admin@localhost:5432/face_detect_db", echo=True)


async def create_db():
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)

    await engine.dispose()


asyncio.run(create_db())
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_async_session() -> AsyncSession:
    async with async_session() as session:
        yield session
