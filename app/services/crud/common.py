from abc import ABCMeta, abstractmethod

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.async_base import get_async_session
from app.db.base import get_session


class AbstractCRUD(metaclass=ABCMeta):
    @abstractmethod
    async def read_all(self, *args, **kwargs):
        """
        Abstract method to read all entities.
        """
        ...

    @abstractmethod
    async def read_one(self, *args, **kwargs):
        """
        Abstract method to read a single entity.
        """
        ...

    @abstractmethod
    async def create(self, *args, **kwargs):
        """
        Abstract method to create an entity.
        """
        ...

    @abstractmethod
    async def update(self, *args, **kwargs):
        """
        Abstract method to update an entity.
        """
        ...

    @abstractmethod
    async def delete(self, *args, **kwargs):
        """
        Abstract method to delete an entity.
        """
        ...


class CRUD(AbstractCRUD, metaclass=ABCMeta):
    """
    A concrete class implementing CRUD operations using SQLAlchemy sessions.

    Attributes:
        session (AsyncSession): The SQLAlchemy session used for database operations.

    Methods:
        - __init__(session: Session = Depends(get_session)): Initializes the CRUD class with the provided SQLAlchemy session.
        - read_all(*args, **kwargs): Implements the method to read all entities.
        - read_one(*args, **kwargs): Implements the method to read a single entity.
        - create(*args, **kwargs): Implements the method to create an entity.
        - update(*args, **kwargs): Implements the method to update an entity.
        - delete(*args, **kwargs): Implements the method to delete an entity.
    """

    def __init__(self, session: AsyncSession = Depends(get_async_session)):
        """
        Initializes the CRUD class with the provided SQLAlchemy session.

        Parameters:
            session (AsyncSession): The SQLAlchemy session to use for database operations.
        """
        self.session = session
