import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status
from pydantic import Field

from app.dependencies.unitofwork import UOWDep
from app.dependencies.users import get_current_user
from app.models.users import User
from app.schemas.base import ErrorEnvelopeModel, SuccessResponseModel
from app.schemas.company import SCompanyCurrent, SCompanyProjectStatuses
from app.services.company import CompanyService
from app.wrappers.api import api_exception_handler

router = APIRouter(prefix="/company", tags=["Company"])

@router.get(
    "/dashboard/status/{company_id}", 
    summary="Получить статус проектов в компании", 
    status_code=status.HTTP_200_OK
    )
@api_exception_handler
async def get_status_projects(
    uow: UOWDep, 
    company_id: uuid.UUID,
    user: User = Depends(get_current_user)
) -> Annotated[SuccessResponseModel[list[SCompanyProjectStatuses]] | ErrorEnvelopeModel, Field(discriminator="status")]:
    """
    **Получить статус проектов в компании**
    
    `company_id` - id компании у которой получаем проекты
    """
    return await CompanyService().get_status_projects(uow, company_id, user), 200

@router.get(
    "/current", 
    summary="Получить текущую компанию", 
    status_code=status.HTTP_200_OK
    )
@api_exception_handler
async def get_current_company(
    uow: UOWDep, 
    user: User = Depends(get_current_user)
) -> Annotated[SuccessResponseModel[SCompanyCurrent] | ErrorEnvelopeModel, Field(discriminator="status")]:
    """
    **Получить текущую компанию**
    """
    return await CompanyService().get_current_company(uow, user), 200