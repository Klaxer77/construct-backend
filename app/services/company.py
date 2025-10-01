import uuid

from app.dependencies.unitofwork import UnitOfWork
from app.exceptions.company import CompanyNotFoundExc
from app.models.company import Company
from app.models.users import User
from app.schemas.company import SCompanyCurrent, SCompanyProjectStatuses


class CompanyService:
    
    async def get_current_company(
        self, 
        uow: UnitOfWork, 
        user: User
        ) -> SCompanyCurrent:
        async with uow:
            company = await uow.company.find_one_or_none(id=user.company_id)
            return SCompanyCurrent.model_validate(company)
    
    async def get_status_projects(
        self, 
        uow: UnitOfWork, 
        company_id: uuid.UUID, 
        user: User
        ) -> list[SCompanyProjectStatuses]:
        async with uow:
            check_company: Company | None = await uow.company.find_one_or_none(id=company_id)
            if not check_company:
                raise CompanyNotFoundExc
            
            projects = await uow.objects.get_status_projects(company_id, user)
            return [SCompanyProjectStatuses.model_validate(p) for p in projects]