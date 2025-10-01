import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, UploadFile, status
from pydantic import Field

from app.dependencies.unitofwork import UOWDep
from app.dependencies.users import get_current_user
from app.models.users import User
from app.schemas.base import ErrorEnvelopeModel, SuccessResponseModel
from app.schemas.control_materials import (
    SCreateMaterials,
    SLlmResponse,
    SMaterials,
    SMaterialsList,
    SMaterialsListDetail,
)
from app.services.control_materials import MaterialService
from app.wrappers.api import api_exception_handler

router = APIRouter(prefix="/materials", tags=["Materials"])

@router.post("/llm", summary="Контроль материалов с llm", status_code=status.HTTP_200_OK)
@api_exception_handler
async def llm(
    upload_file: UploadFile,
    user: User = Depends(get_current_user)
) -> Annotated[SuccessResponseModel[SLlmResponse] | ErrorEnvelopeModel, Field(discriminator="status")]:
    """
    **Контроль материалов с llm**
    
    `upload_file` - файл для распознавания
    """
    return await MaterialService().llm(upload_file), 200

@router.post("/add/{object_id}", summary="Добавить материалы", status_code=status.HTTP_201_CREATED)
@api_exception_handler
async def create_material(
    uow: UOWDep,
    user_data: SCreateMaterials,
    category_id: uuid.UUID,
    object_id: uuid.UUID,
    user: User = Depends(get_current_user)
) -> Annotated[SuccessResponseModel[SMaterials] | ErrorEnvelopeModel, Field(discriminator="status")]:
    """
    **Добавить материалы**
    """
    return await MaterialService().create_material(
        uow, 
        user_data, 
        category_id,
        object_id
        ), 201
 
    
@router.get(
    "/list", 
    summary="Получить категории материалов", 
    status_code=status.HTTP_200_OK
)
@api_exception_handler
async def list_materials(
    uow: UOWDep,
    user: User = Depends(get_current_user)
) -> Annotated[SuccessResponseModel[list[SMaterialsList]] | ErrorEnvelopeModel, Field(discriminator="status")]:
    """
    **Получить категории материалов**
    """
    return await MaterialService().list_materials(uow), 200

@router.get(
    "/list/detail/{object_id}/{category_id}", 
    summary="Получить внесенные материалы объекта в конкретной категории", 
    status_code=status.HTTP_200_OK
)
@api_exception_handler
async def list_materials_detail(
    uow: UOWDep,
    object_id: uuid.UUID,
    category_id: uuid.UUID,
    user: User = Depends(get_current_user)
) -> Annotated[SuccessResponseModel[list[SMaterialsListDetail]] | ErrorEnvelopeModel, Field(discriminator="status")]:
    """
    **Получить внесенные материалы объекта в конкретной категории**
    """
    return await MaterialService().list_materials_detail(uow, object_id, category_id), 200