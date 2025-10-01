from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company import Company
from app.repositories.base import SQLAlchemyRepository


class CompanyRepository(SQLAlchemyRepository):
    model = Company

    def __init__(self, session: AsyncSession):
        self.session = session