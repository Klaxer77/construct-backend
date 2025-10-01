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
from app.schemas.remarks import (
    SRemark,
    SRemarkAnswer,
    SRemarkAnswerCreate,
    SRemarkChangedSuccess,
    SRemarkChangeStatus,
    SRemarkCreate,
    SRemarksDetail,
    SRemarksList,
)
from app.services.remarks import RemarksService
from app.wrappers.api import api_exception_handler

router = APIRouter(prefix="/remarks", tags=["Remarks"])

@router.post("/create/{object_id}", summary="Создать замечание", status_code=status.HTTP_201_CREATED)
@api_exception_handler
async def create_remark(
    uow: UOWDep,
    object_id: uuid.UUID,
    latitude: float = Header(..., description="Широта"),
    longitude: float = Header(..., description="Долгота"),
    user_data: str = Form(...),
    files: list[UploadFile] = File(None),
    user: User = Depends(get_current_user)
) -> Annotated[SuccessResponseModel[list[SRemark]] | ErrorEnvelopeModel, Field(discriminator="status")]:
    """
    **Создать замечание**
    
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
    
    `object_id` - id объекта к которому создаем замечание
    
    `files` - список загружаемых файлов
    """
    try:
        remark_list = json.loads(user_data)
        remarks_data = [SRemarkCreate(**item) for item in remark_list]
        return await RemarksService().create_remark(
            uow, 
            remarks_data, 
            files, 
            object_id,
            user,
            latitude,
            longitude
            ), 201
    except ValidationError as e:
        raise RequestValidationError(errors=jsonable_encoder(e.errors()))
    
@router.get(
    "/all/{object_id}", 
    summary="Получить все замечания", 
    status_code=status.HTTP_200_OK
    )
@api_exception_handler
async def get_all_remarks(
    uow: UOWDep, 
    object_id: uuid.UUID,
    user: User = Depends(get_current_user)
) -> Annotated[SuccessResponseModel[list[SRemarksList]] | ErrorEnvelopeModel, Field(discriminator="status")]:
    """
    **Получить все замечания**
    
    `object_id` - id объекта для которого получаем замечания
    """
    return await RemarksService().get_all_remarks(uow, object_id), 200

@router.get(
    "/detail/{remark_id}", 
    summary="Получить конкретное замечание", 
    status_code=status.HTTP_200_OK
    )
@api_exception_handler
async def get_remarks_detail(
    uow: UOWDep, 
    remark_id: uuid.UUID,
    user: User = Depends(get_current_user)
) -> Annotated[SuccessResponseModel[SRemarksDetail] | ErrorEnvelopeModel, Field(discriminator="status")]:
    """
    **Получить конкретное замечание**
    
    `remark_id` - id получаемого замечания
    """
    return await RemarksService().get_remarks_detail(uow, remark_id), 200


@router.post(
    "/change/status/{remark_id}", 
    summary="Принять/отклонить под замечание", 
    status_code=status.HTTP_200_OK
    )
@api_exception_handler
async def remarks_change_status(
    uow: UOWDep,
    user_data: SRemarkChangeStatus, 
    remark_id: uuid.UUID,
    user: User = Depends(get_current_user)
) -> Annotated[SuccessResponseModel[SRemarkChangedSuccess] | ErrorEnvelopeModel, Field(discriminator="status")]:
    """
    **Принять/отклонить под замечание**
    
    `remark_id` - id изменяемого под замечания
    
    `action` - действие _only accept, deny_
    """
    return await RemarksService().remarks_change_status(uow, remark_id, user_data), 200

@router.post(
    "/answer/{remark_id}/{object_id}", 
    summary="Ответить на конкретное под замечание", 
    status_code=status.HTTP_201_CREATED
    )
@api_exception_handler
async def answer_remarks(
    uow: UOWDep, 
    remark_id: uuid.UUID,
    object_id: uuid.UUID,
    user_data: str = Form(...),
    files: list[UploadFile] = File(None),
    user: User = Depends(get_current_user)
) -> Annotated[SuccessResponseModel[SRemarkAnswer] | ErrorEnvelopeModel, Field(discriminator="status")]:
    """
    **Ответить на конкретное под замечание**
    
    `user_data` example - {
        "comment": "comment"
    }
    
    `comment` - строка | null
    
    `remark_id` - id получаемого под замечания
    
    `object_id` - id объекта замечания
    
    `files` - прикрепляемые файлы
    """
    try:
        remark_dict = json.loads(user_data)
        remark_data = SRemarkAnswerCreate(**remark_dict)
        return await RemarksService().answer_remarks(
            uow, 
            remark_data, 
            files, 
            remark_id,
            object_id,
            user
            ), 201
    except ValidationError as e:
        raise RequestValidationError(errors=jsonable_encoder(e.errors()))