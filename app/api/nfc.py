import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status
from pydantic import Field

from app.dependencies.unitofwork import UOWDep
from app.dependencies.users import get_current_user
from app.models.users import User
from app.schemas.base import ErrorEnvelopeModel, SuccessResponseModel
from app.schemas.nfc import (
    SNFCADD,
    SNFCChange,
    SNFCCreate,
    SNFCDelete,
    SNFCHistoryObject,
    SNFCHistoryObjectList,
    SNFCSessionTerminate,
    SNFCVerify,
)
from app.services.nfc import NFCService
from app.wrappers.api import api_exception_handler

router = APIRouter(prefix="/nfc", tags=["NFC"])

@router.post("/add/{object_id}", summary="Добавить nfc для объекта", status_code=status.HTTP_201_CREATED)
@api_exception_handler
async def create_nfc(
    uow: UOWDep, 
    user_data: SNFCCreate,
    object_id: uuid.UUID,
    user: User = Depends(get_current_user)
) -> Annotated[SuccessResponseModel[SNFCADD] | ErrorEnvelopeModel, Field(discriminator="status")]:
    """
    **Добавить nfc для объекта**
    
    `nfc_uid` - Уникальный uid от сканированного NFC
    
    `object_id` - id объекта для которого создаем новую nfc
    """
    return await NFCService().create(uow, user_data, object_id, user), 201

@router.patch("/change/{nfc_id}/{object_id}", summary="Изменить название nfc", status_code=status.HTTP_200_OK)
@api_exception_handler
async def change_nfc(
    uow: UOWDep, 
    nfc_id: uuid.UUID,
    object_id: uuid.UUID,
    user_data: SNFCChange,
    user: User = Depends(get_current_user)
) -> Annotated[SuccessResponseModel[SNFCChange] | ErrorEnvelopeModel, Field(discriminator="status")]:
    """
    **Изменить название nfc**
    
    `nfc_id` - id nfc
    
    `object_id` - id объекта у которого изменяем nfc
    """
    return await NFCService().change_nfc(uow, nfc_id, object_id, user_data), 200


@router.post("/verify/{object_id}", summary="Верификация по nfc", status_code=status.HTTP_201_CREATED)
@api_exception_handler
async def verify_nfc(
    uow: UOWDep, 
    user_data: SNFCCreate,
    object_id: uuid.UUID,
    user: User = Depends(get_current_user)
) -> Annotated[SuccessResponseModel[SNFCVerify] | ErrorEnvelopeModel, Field(discriminator="status")]:
    """
    **Верификация по nfc**
    
    `nfc_uid` - Уникальный uid от сканированного NFC
    
    `object_id` - id объекта у которого верифицируемся
    """
    return await NFCService().verify_nfc(uow, user_data, user, object_id), 201


@router.get(
    "/history/{object_id}", 
    summary="Получить историю верификаций nfc конкретного объекта", 
    status_code=status.HTTP_200_OK
    )
@api_exception_handler
async def history_nfc(
    uow: UOWDep, 
    object_id: uuid.UUID,
    user: User = Depends(get_current_user)
) -> Annotated[SuccessResponseModel[list[SNFCHistoryObject]] | ErrorEnvelopeModel, Field(discriminator="status")]:
    """
    **Получить историю верификаций nfc конкретного объекта**
    
    `object_id` - id объекта у которого получаем историю верификаций
    """
    return await NFCService().history_nfc(uow, object_id, user), 200


@router.get("/history", summary="Получить всю историю верификаций nfc", status_code=status.HTTP_200_OK)
@api_exception_handler
async def history_nfc_all(
    uow: UOWDep, 
    user: User = Depends(get_current_user)
) -> Annotated[SuccessResponseModel[list[SNFCHistoryObject]] | ErrorEnvelopeModel, Field(discriminator="status")]:
    """
    **Получить всю историю верификаций nfc**
    """
    return await NFCService().history_nfc_all(uow, user), 200

@router.post("/session/{object_id}", summary="Завершить сессию nfc", status_code=status.HTTP_200_OK)
@api_exception_handler
async def session_nfc(
    uow: UOWDep,
    object_id: uuid.UUID,
    user: User = Depends(get_current_user)
) -> Annotated[SuccessResponseModel[SNFCSessionTerminate] | ErrorEnvelopeModel, Field(discriminator="status")]:
    """
    **Завершить сессию nfc**
    """
    return await NFCService().session_nfc(uow, object_id, user), 200

@router.get("/all/{object_id}", summary="Получить установленные nfc объекта", status_code=status.HTTP_200_OK)
@api_exception_handler
async def all_nfc(
    uow: UOWDep, 
    object_id: uuid.UUID
) -> Annotated[SuccessResponseModel[list[SNFCHistoryObjectList]] | ErrorEnvelopeModel, Field(discriminator="status")]:
    """
    **Получить установленные nfc объекта**
    
    `object_id` - id объекта у которого получаем установленные метки
    """
    return await NFCService().all_nfc(uow, object_id), 200


@router.delete("/delete/{nfc_id}", summary="Удалить nfc", status_code=status.HTTP_200_OK)
@api_exception_handler
async def delete_nfc(
    uow: UOWDep, 
    nfc_id: uuid.UUID,
    user: User = Depends(get_current_user)
) -> Annotated[SuccessResponseModel[SNFCDelete] | ErrorEnvelopeModel, Field(discriminator="status")]:
    """
    **Удалить nfc**
    
    `nfc_id` - id удаляемой nfc
    """
    return await NFCService().delete_nfc(uow, nfc_id), 200