import json
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from pydantic import Field, ValidationError

from app.dependencies.unitofwork import UOWDep
from app.dependencies.users import get_current_user
from app.models.users import User
from app.schemas.base import ErrorEnvelopeModel, SuccessResponseModel
from app.schemas.control_materials import (
    SCreateDeliveryWorks,
    SCreateMaterials,
    SDetailStageWork,
    SLlmResponse,
    SMaterials,
    SMaterialsWorkCreate,
    SMaterialsWorkRead,
    SProgressObject,
    SWorkAction,
    SWorkBegin,
    SWorkChangeStatus,
    SWorkDelivery,
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

@router.post("/add/{stage_progress_work_id}", summary="Добавить материалы", status_code=status.HTTP_201_CREATED)
@api_exception_handler
async def create_material(
    uow: UOWDep,
    user_data: SCreateMaterials,
    stage_progress_work_id: uuid.UUID,
    user: User = Depends(get_current_user)
) -> Annotated[SuccessResponseModel[SMaterials] | ErrorEnvelopeModel, Field(discriminator="status")]:
    """
    **Добавить материалы**
    """
    return await MaterialService().create_material(
        uow, 
        user_data,
        stage_progress_work_id
        ), 201
 
    
@router.get(
    "/list/work", 
    summary="Получить все ходы работ объекта", 
    status_code=status.HTTP_200_OK
)
@api_exception_handler
async def list_work(
    uow: UOWDep,
    object_id: uuid.UUID,
    user: User = Depends(get_current_user)
) -> Annotated[SuccessResponseModel[list[SMaterialsWorkRead]] | ErrorEnvelopeModel, Field(discriminator="status")]:
    """
    **Получить все ходы работ объекта**
    """
    return await MaterialService().list_work(uow, object_id), 200

@router.get(
    "/list/{stage_progress_work_id}", 
    summary="Получить внесенные материалы хода работ", 
    status_code=status.HTTP_200_OK
)
@api_exception_handler
async def list_materials_stage(
    uow: UOWDep,
    stage_progress_work_id: uuid.UUID,
    user: User = Depends(get_current_user)
) -> Annotated[SuccessResponseModel[list[SMaterials]] | ErrorEnvelopeModel, Field(discriminator="status")]:
    """
    **Получить внесенные материалы хода работ**
    """
    return await MaterialService().list_materials_stage(uow, stage_progress_work_id), 200

@router.get(
    "/progress/{object_id}", 
    summary="Получить общий прогресс хода работ объекта", 
    status_code=status.HTTP_200_OK
)
@api_exception_handler
async def object_progress(
    uow: UOWDep,
    object_id: uuid.UUID,
    user: User = Depends(get_current_user)
) -> Annotated[SuccessResponseModel[SProgressObject] | ErrorEnvelopeModel, Field(discriminator="status")]:
    """
    **Получить общий прогресс хода работ объекта**
    """
    return await MaterialService().object_progress(uow, object_id), 200


@router.get(
    "/list/work/{stage_progress_work_id}", 
    summary="Получить конкретный перечень работ", 
    status_code=status.HTTP_200_OK
)
@api_exception_handler
async def detail_stage_work(
    uow: UOWDep,
    stage_progress_work_id: uuid.UUID,
    user: User = Depends(get_current_user)
) -> Annotated[SuccessResponseModel[SDetailStageWork] | ErrorEnvelopeModel, Field(discriminator="status")]:
    """
    **Получить конкретный перечень работ**
    """
    return await MaterialService().detail_stage_work(uow, stage_progress_work_id), 200


@router.post(
    "/create/works", 
    summary="Создать ход работ", 
    status_code=status.HTTP_201_CREATED
)
@api_exception_handler
async def create_work(
    uow: UOWDep,
    object_id: uuid.UUID,
    user_data: SMaterialsWorkCreate,
    user: User = Depends(get_current_user)
) -> Annotated[SuccessResponseModel[SMaterialsWorkRead] | ErrorEnvelopeModel, Field(discriminator="status")]:
    """
    **Создать ход работ**
    """
    return await MaterialService().create_work(uow, object_id, user_data), 201

@router.post(
    "/begin/works", 
    summary="Начать ход работ", 
    status_code=status.HTTP_200_OK
)
@api_exception_handler
async def begin_work(
    uow: UOWDep,
    stage_progress_work_id: uuid.UUID,
    user: User = Depends(get_current_user)
) -> Annotated[SuccessResponseModel[SWorkBegin] | ErrorEnvelopeModel, Field(discriminator="status")]:
    """
    **Начать ход работ**
    """
    return await MaterialService().begin_work(uow, stage_progress_work_id), 200


@router.post(
    "/works/pass", 
    summary="Сдать часть работ", 
    status_code=status.HTTP_201_CREATED
)
@api_exception_handler
async def delivery_work(
    uow: UOWDep,
    stage_progress_work_id: uuid.UUID,
    user_data: str = Form(...),
    files: list[UploadFile] = File(None),
    user: User = Depends(get_current_user)
) -> Annotated[SuccessResponseModel[SWorkDelivery] | ErrorEnvelopeModel, Field(discriminator="status")]:
    """
    **Сдать часть работ**
    
    `user_data` example - {
        "volume": 100,
        "desc": "desc",
        "photos_keys": ["photo1.png", "photo2.png"]
    }
    """
    try:
        work_dict = json.loads(user_data)
        work_data = SCreateDeliveryWorks(**work_dict)
        return await MaterialService().delivery_work(
            uow,
            work_data,
            stage_progress_work_id,
            files
            ), 201
    except ValidationError as e:
        raise RequestValidationError(errors=jsonable_encoder(e.errors()))
    
@router.post(
    "/action/works", 
    summary="Принять или отклонить ход работ", 
    status_code=status.HTTP_201_CREATED
)
@api_exception_handler
async def action_work(
    uow: UOWDep,
    user_data: SWorkChangeStatus,
    list_of_work_id: uuid.UUID,
    user: User = Depends(get_current_user)
) -> Annotated[SuccessResponseModel[SWorkAction] | ErrorEnvelopeModel, Field(discriminator="status")]:
    """
    **Принять или отклонить ход работ**
    """
    return await MaterialService().action_work(uow, list_of_work_id, user_data), 201