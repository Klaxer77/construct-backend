import json
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, Header, UploadFile, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from pydantic import Field, ValidationError

from app.dependencies.unitofwork import UOWDep
from app.dependencies.users import get_current_user
from app.models.users import User
from app.schemas.base import ErrorEnvelopeModel, SuccessResponseModel
from app.schemas.violations import (
    SVialationAnswer,
    SVialationAnswerCreate,
    SViolation,
    SViolationChangedSuccess,
    SViolationChangeStatus,
    SViolationCreate,
    SViolationsDetail,
    SViolationsList,
)
from app.services.violations import ViolationsService
from app.wrappers.api import api_exception_handler

router = APIRouter(prefix="/violations", tags=["Violations"])

@router.post("/create/{object_id}", summary="Создать нарушение", status_code=status.HTTP_201_CREATED)
@api_exception_handler
async def create_violation(
    uow: UOWDep,
    object_id: uuid.UUID,
    user_data: str = Form(...),
    latitude: float = Header(..., description="Широта"),
    longitude: float = Header(..., description="Долгота"), 
    files: list[UploadFile] = File(None),
    user: User = Depends(get_current_user)
) -> Annotated[SuccessResponseModel[list[SViolation]] | ErrorEnvelopeModel, Field(discriminator="status")]:
    """
    **Создать нарушение**
    
    `latitude` - широта
    
    `longitude` - долгота
    
    `user_data` example - [
        {
            "violations": "Нет каски у работника",
            "name_regulatory_docx": "Правила охраны труда",
            "expiration_date": "2025-09-24T12:00:00Z",
            "comment": "Нужно выдать каску",
            "photos_keys": ["photo1.png", "photo2.png"]
        },   
        {
            "violations": "Открытые провода",
            "name_regulatory_docx": "ГОСТ 123-456",
            "expiration_date": "2025-09-24T13:30:00Z",
            "comment": "Закрыть кабель-каналом",
            "photos_keys": ["photo3.png"]
        } 
        ]
    
    `violations` - перечень выявленных нарушений
    
    `name_regulatory_docx` - наименование нормативного документа
    
    `expiration_date` - срок устранения
    
    `comment` - комментарий
        
    `photos_keys` - обязательно передавать полные названия файлов с расширениями
    
    `object_id` - id объекта к которому создаем нарушение
    
    `files` - список загружаемых файлов
    """
    try:
        violation_list = json.loads(user_data)
        violations_data = [SViolationCreate(**item) for item in violation_list]
        return await ViolationsService().create_violation(
            uow, 
            violations_data, 
            files, 
            object_id,
            latitude,
            longitude,
            user
            ), 201
    except ValidationError as e:
        raise RequestValidationError(errors=jsonable_encoder(e.errors()))
    
@router.get(
    "/all/{object_id}", 
    summary="Получить все нарушения", 
    status_code=status.HTTP_200_OK
    )
@api_exception_handler
async def get_all_violations(
    uow: UOWDep, 
    object_id: uuid.UUID,
    user: User = Depends(get_current_user)
) -> Annotated[SuccessResponseModel[list[SViolationsList]] | ErrorEnvelopeModel, Field(discriminator="status")]:
    """
    **Получить все нарушения**
    
    `object_id` - id объекта для которого получаем нарушения
    """
    return await ViolationsService().get_all_violations(uow, object_id), 200

@router.get(
    "/detail/{violation_id}", 
    summary="Получить конкретное нарушение", 
    status_code=status.HTTP_200_OK
    )
@api_exception_handler
async def get_violations_detail(
    uow: UOWDep, 
    violation_id: uuid.UUID,
    user: User = Depends(get_current_user)
) -> Annotated[SuccessResponseModel[SViolationsDetail] | ErrorEnvelopeModel, Field(discriminator="status")]:
    """
    **Получить конкретное нарушение**
    
    `violation_id` - id получаемого нарушения
    """
    return await ViolationsService().get_violations_detail(uow, violation_id), 200


@router.post(
    "/change/status/{violation_id}", 
    summary="Принять/отклонить под нарушение", 
    status_code=status.HTTP_200_OK
    )
@api_exception_handler
async def violations_change_status(
    uow: UOWDep,
    user_data: SViolationChangeStatus, 
    violation_id: uuid.UUID,
    user: User = Depends(get_current_user)
) -> Annotated[SuccessResponseModel[SViolationChangedSuccess] | ErrorEnvelopeModel, Field(discriminator="status")]:
    """
    **Принять/отклонить под нарушение**
    
    `violation_id` - id изменяемого нарушения
    
    `action` - действие _only accept, deny_
    """
    return await ViolationsService().violations_change_status(uow, violation_id, user_data), 200

@router.post(
    "/answer/{vialation_id}/{object_id}", 
    summary="Ответить на конкретное под нарушение", 
    status_code=status.HTTP_201_CREATED
    )
@api_exception_handler
async def answer_vialations(
    uow: UOWDep, 
    vialation_id: uuid.UUID,
    object_id: uuid.UUID,
    user_data: str = Form(...),
    files: list[UploadFile] = File(None),
    user: User = Depends(get_current_user)
) -> Annotated[SuccessResponseModel[SVialationAnswer] | ErrorEnvelopeModel, Field(discriminator="status")]:
    """
    **Ответить на конкретное под нарушение**
    
    `user_data` example - {
        "comment": "comment"
    }
    
    `comment` - строка | null
    
    `remark_id` - id получаемого под нарушения
    
    `object_id` - id объекта замечания
    
    `files` - прикрепляемые файлы
    """
    try:
        remark_dict = json.loads(user_data)
        remark_data = SVialationAnswerCreate(**remark_dict)
        return await ViolationsService().answer_vialation(
            uow, 
            remark_data, 
            files, 
            vialation_id,
            object_id,
            user
            ), 201
    except ValidationError as e:
        raise RequestValidationError(errors=jsonable_encoder(e.errors()))