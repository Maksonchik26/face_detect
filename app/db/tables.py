from typing import List

from sqlalchemy import ForeignKey, JSON, String, Integer, Float
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class UpdateMixin:
    def update_entity(self, **kwargs):
        for field, value in kwargs.items():
            if hasattr(self, field):
                setattr(self, field, value)


class BaseModel(DeclarativeBase, UpdateMixin):
    pass


class Task(BaseModel):
    __tablename__ = "task"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(256), unique=True, nullable=False)
    total_persons: Mapped[int] = mapped_column(Integer(), nullable=True)
    total_males: Mapped[int] = mapped_column(Integer(), nullable=True)
    total_females: Mapped[int] = mapped_column(Integer(), nullable=True)
    average_male_age: Mapped[int] = mapped_column(Float(), nullable=True)
    average_female_age: Mapped[int] = mapped_column(Float(), nullable=True)
    status: Mapped[str] = mapped_column(String(64), default="Created")
    # relations
    images: Mapped[List["Image"]] = relationship(back_populates="task", cascade="all, delete")


class Image(BaseModel):
    __tablename__ = "image"
    id: Mapped[int] = mapped_column(Integer(), primary_key=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    # parent
    task_id: Mapped[int] = mapped_column(ForeignKey("task.id", ondelete="CASCADE"))
    # relations
    task: Mapped["Task"] = relationship(back_populates="images")
    persons: Mapped[List["Person"]] = relationship(back_populates="image", cascade="all, delete")


class Person(BaseModel):
    __tablename__ = "person"
    id: Mapped[int] = mapped_column(Integer(), primary_key=True)
    bounding_box: Mapped[dict] = mapped_column(JSON)
    gender: Mapped[str] = mapped_column(String(64))
    age: Mapped[int] = mapped_column(Integer())
    # parent
    image_id: Mapped[int] = mapped_column(ForeignKey("image.id", ondelete="CASCADE"))
    # relations
    image: Mapped["Image"] = relationship(back_populates="persons")
