from typing import TypeVar

from sqlalchemy import delete, func, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")

class SQLAlchemyRepository:
    model = type[T]

    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def count_by_filter(self, **filters) -> int:
        query = select(func.count()).select_from(self.model).filter_by(**filters)
        result = await self.session.execute(query)
        return result.scalar_one()
    
    async def count_all(self) -> int:
        """Подсчитать все сущности"""
        query = select(func.count()).select_from(self.model)
        result = await self.session.execute(query)
        return result.scalar_one()

    async def get_all(self) -> list[T]:
        """Получить список всех сущностей."""
        query = select(self.model)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def delete_by_filter(self, *filter, **filter_by) -> T:
        """Удалить сущность по фильтру"""
        query = delete(self.model).filter(*filter).filter_by(**filter_by).returning(self.model)
        result = await self.session.execute(query)
        return result.scalars().one()

    async def insert_by_data(self, entity_data: dict) -> T | None:
        """Добавить сущность"""
        query = insert(self.model).values(entity_data).returning(self.model)
        result = await self.session.execute(query)
        return result.scalars().one()

    async def update_by_filter(self, update_data: dict, *filter, **filter_by) -> T:
        """Обновить сущность по фильтру"""
        query = (
            update(self.model)
            .filter(*filter)
            .filter_by(**filter_by)
            .values(**update_data)
            .returning(self.model)
        )
        result = await self.session.execute(query)
        return result.scalars().one()
    
    async def update_many_by_filter(self, update_data: dict, *filter, **filter_by) -> T:
        """Обновить сущность по фильтру"""
        query = (
            update(self.model)
            .filter(*filter)
            .filter_by(**filter_by)
            .values(**update_data)
        )
        await self.session.execute(query)
        return None

    async def find_one_or_none(self, **filter_by) -> T | None:
        """Найти сущность по фильтру"""
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)
        return result.scalars().one_or_none()

    async def find_all(self, **filter_by) -> list[T]:
        """Найти все сущности, удовлетворяющие фильтру"""
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def find_all_by_filter(self, **filter_by) -> list[T]:
        """Найти все сущности, удовлетворяющие фильтру"""
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)
        return result.scalars().all()
