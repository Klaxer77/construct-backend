from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.control_materials import CategoriesMaterials, Materials
from app.repositories.base import SQLAlchemyRepository


class MaterialsRepository(SQLAlchemyRepository):
    model = Materials

    def __init__(self, session: AsyncSession):
        self.session = session
        

class CategoriesMaterialsRepository(SQLAlchemyRepository):
    model = CategoriesMaterials

    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def list_materials(self) -> list[CategoriesMaterials]:
        stmt = (
            select(CategoriesMaterials)
            .options(selectinload(CategoriesMaterials.subcategories))
            .where(CategoriesMaterials.parent_id.is_(None))
            .distinct()
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
