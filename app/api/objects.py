import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, File, Header, UploadFile, status
from pydantic import Field

from app.dependencies.unitofwork import UOWDep
from app.dependencies.users import get_current_user
from app.models.enums import ActObjectsActionEnum, ObjectTypeEnum, ObjectTypeFilter
from app.models.users import User
from app.schemas.base import ErrorEnvelopeModel, SuccessResponseModel
from app.schemas.objects import (
    SActCreate,
    SActDetail,
    SActSuccessCreated,
    SCategoriesObjects,
    SCountObjects,
    SObject,
    SObjectCreate,
    SObjectDetail,
    SObjectGEOCheck,
    SObjectsList,
    SObjectUpdated,
)
from app.services.objects import ObjectsService
from app.wrappers.api import api_exception_handler

router = APIRouter(prefix="/objects", tags=["Objects"])

@router.post("/create/{company_id}", summary="Создать объект", status_code=status.HTTP_201_CREATED)
@api_exception_handler
async def create(
    uow: UOWDep, 
    company_id: uuid.UUID,
    user_data: SObjectCreate,
    user: User = Depends(get_current_user)
) -> Annotated[SuccessResponseModel[SObject] | ErrorEnvelopeModel, Field(discriminator="status")]:
    """
    **Создать объект**
    
    `company_id` - id компании для которой создаем объект
    
    `general_info` - наименование и адрес объекта | Общие сведения
    
    `title` - Название объекта
    
    `city` - город объекта (из api карт достать или по координатам)
    
    `date_delivery_verification` - дата окончания объекта
    
    `start_date` - дата старта объекта
    
    `coords`: [
        [[37.6173, 55.7558], [37.6180, 55.7560], [37.6175, 55.7565], [37.6173, 55.7558]],
        [[37.6190, 55.7560], [37.6200, 55.7565], [37.6195, 55.7570], [37.6190, 55.7560]]
    ] - Мульти полигон
  
    `coords`: [
        [37.6173, 55.7558],
        [37.6180, 55.7560],
        [37.6175, 55.7565],
        [37.6173, 55.7558]
    ] - Обычный полигон
    """
    return await ObjectsService().create(uow, user_data, user, company_id), 201

@router.get(
    "/{object_id}", 
    summary="Получить конкретный объект", 
    status_code=status.HTTP_200_OK
    )
@api_exception_handler
async def get_object_detail(
    uow: UOWDep, 
    object_id: uuid.UUID,
    user: User = Depends(get_current_user)
) -> Annotated[SuccessResponseModel[SObjectDetail] | ErrorEnvelopeModel, Field(discriminator="status")]:
    """
    **Получить конкретный объект**
    
    `object_id` - id получаемого объекта
    """
    return await ObjectsService().get_object_detail(uow, object_id), 200

@router.get(
    "/count/{filter_by}/{company_id}", 
    summary="Получить общее количество объектов по фильтру", 
    status_code=status.HTTP_200_OK
    )
@api_exception_handler
async def count_objects(
    uow: UOWDep, 
    filter_by: ObjectTypeEnum,
    company_id: uuid.UUID,
    category_id: uuid.UUID | None = None,
    user: User = Depends(get_current_user)
) -> Annotated[SuccessResponseModel[SCountObjects] | ErrorEnvelopeModel, Field(discriminator="status")]:
    """
    **Получить общее количество объектов по фильтру**
    
    `filter_by` - _active_ - активные, _not_active_ - неактивные, _agreement_ - на согласовании, _act_opening_ - требуется акт открытия
    
    `category_id` - id категории передаем из запроса /api/v1/objects/categories, если нужна фильтрация не по "Все" (для хардкора создается только объект категории "Жилые"), если нужна фильтрация "Все" передаем null
    """ #noqa
    return await ObjectsService().count_objects(uow, category_id, filter_by, company_id, user), 200

@router.get(
    "/categories", 
    summary="Получить все категории объектов", 
    status_code=status.HTTP_200_OK
    )
@api_exception_handler
async def get_all_categories_objects(
    uow: UOWDep, 
    user: User = Depends(get_current_user)
) -> Annotated[SuccessResponseModel[list[SCategoriesObjects]] | ErrorEnvelopeModel, Field(discriminator="status")]:
    """
    **Получить все категории объектов**
    """
    return await ObjectsService().get_all_categories_objects(uow), 200

@router.get(
    "/all/{filter_by}/{company_id}", 
    summary="Получить все объекты по фильтру", 
    status_code=status.HTTP_200_OK
    )
@api_exception_handler
async def get_all_objects_by_filter(
    uow: UOWDep, 
    filter_by: ObjectTypeFilter,
    company_id: uuid.UUID,
    user: User = Depends(get_current_user)
) -> Annotated[SuccessResponseModel[list[SObjectsList]] | ErrorEnvelopeModel, Field(discriminator="status")]:
    """
    **Получить все объекты по фильтру**
    
    `filter_by` - _all_ - получаем все, _active_ - активные, _not_active_ - неактивные, _agreement_ - на согласовании, _act_opening_ - требуется акт открытия
    """ #noqa
    return await ObjectsService().get_all_objects_by_filter(uow, filter_by, company_id, user), 200

@router.post(
    "/send/file/{object_id}", 
    summary="Отправить файл для активации", 
    status_code=status.HTTP_201_CREATED
    )
@api_exception_handler
async def send_file(
    uow: UOWDep, 
    object_id: uuid.UUID,
    upload_file: UploadFile = File(...),
    user: User = Depends(get_current_user)
) -> Annotated[SuccessResponseModel[SActSuccessCreated] | ErrorEnvelopeModel, Field(discriminator="status")]:
    """
    **Отправить файл для активации**
    
    `object_id` - id объекта к которому отправляем файл
    
    `upload_file` - отправляемый файл
    """
    return await ObjectsService().send_file(uow, object_id, upload_file), 201

@router.post(
    "/activate/checkList/{object_id}", 
    summary="Создать чек лист активации объекта", 
    status_code=status.HTTP_201_CREATED
    )
@api_exception_handler
async def activate_object_check_list(
    uow: UOWDep, 
    user_data: SActCreate,
    object_id: uuid.UUID,
    user: User = Depends(get_current_user)
) -> Annotated[SuccessResponseModel[SActSuccessCreated] | ErrorEnvelopeModel, Field(discriminator="status")]:
    """
    **Создать чек лист активации объекта**
    
    `contractor_id` - id подрядчика (то есть ответственного) из запроса /api/v1/users/contractors
    
    `date_verification` - дата проверки
    
    `act_docx` - 
        `code` - хардкордим на фронте (например: "1.1")
        `title` - хардкордим на фронте (например: "Наличие приказа...")
        `description` - описание
        `status` - выбор пользователя _only:_ yes, no, not_required
    """
    return await ObjectsService().activate_object_check_list(uow, object_id, user_data), 201

@router.post(
    "/act/change/{object_id}", 
    summary="Принять или отменить акт объекта", 
    status_code=status.HTTP_201_CREATED
    )
@api_exception_handler
async def act_change(
    uow: UOWDep, 
    action: ActObjectsActionEnum,
    object_id: uuid.UUID,
    user: User = Depends(get_current_user)
) -> Annotated[SuccessResponseModel[SObjectUpdated] | ErrorEnvelopeModel, Field(discriminator="status")]:
    """
    **Принять или отменить акт объекта**
    
    `object_id` - id объекта которого изменяем
    
    `action` - действие принять или отменить
    """
    return await ObjectsService().act_change(uow, object_id, action), 201

@router.get(
    "/checkList/{object_id}", 
    summary="Получить чек лист активации объекта", 
    status_code=status.HTTP_200_OK
    )
@api_exception_handler
async def object_check_list(
    uow: UOWDep, 
    object_id: uuid.UUID,
    user: User = Depends(get_current_user)
) -> Annotated[SuccessResponseModel[SActDetail] | ErrorEnvelopeModel, Field(discriminator="status")]:
    """
    **Получить чек лист активации объекта**
    
    `object_id` - id объекта
    """
    return await ObjectsService().object_check_list(uow, object_id), 200


@router.get(
    "/check/geo/{object_id}", 
    summary="Проверить гео у объекта", 
    status_code=status.HTTP_200_OK
    )
@api_exception_handler
async def check_geo(
    uow: UOWDep, 
    object_id: uuid.UUID,
    latitude: float = Header(..., description="Широта"),
    longitude: float = Header(..., description="Долгота"), 
    user: User = Depends(get_current_user)
) -> Annotated[SuccessResponseModel[SObjectGEOCheck] | ErrorEnvelopeModel, Field(discriminator="status")]:
    """
    **Проверить гео у объекта**
    
    `object_id` - id объекта у которого проверяем гео
    
    `latitude` - широта
    
    `longitude` - долгота
    """
    return await ObjectsService().check_geo(
        uow, 
        object_id, 
        latitude,
        longitude
        ), 200