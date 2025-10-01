from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response, status
from pydantic import Field

from app.dependencies.unitofwork import UOWDep
from app.dependencies.users import get_current_user
from app.models.users import User
from app.schemas.base import ErrorEnvelopeModel, SuccessResponseModel
from app.schemas.users import SUserCurrent, SUserLogin, SUserLogout, SUserRole, SUsersContractor, SUserTokens
from app.services.users import UsersService
from app.wrappers.api import api_exception_handler

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/login", summary="Вход пользователя в админ панель", status_code=status.HTTP_201_CREATED)
@api_exception_handler
async def login(uow: UOWDep, user_data: SUserLogin, response: Response
) -> Annotated[SuccessResponseModel[SUserCurrent] | ErrorEnvelopeModel, Field(discriminator="status")]:
    """**Вход пользователя в админ панель**"""
    login_data = await UsersService().login(uow, user_data, response)
    return login_data, 201

@router.get("/current", summary="Текущий пользователь", status_code=status.HTTP_200_OK)
@api_exception_handler
async def get_current_user_endppint(uow: UOWDep, user: User = Depends(get_current_user)
) -> Annotated[SuccessResponseModel[SUserCurrent] | ErrorEnvelopeModel, Field(discriminator="status")]:
    """**Текущий пользователь**"""
    return await UsersService().get_current_user(uow, user), 200

@router.get("/role", summary="Получить роль пользователя по email", status_code=status.HTTP_200_OK)
@api_exception_handler
async def get_user_role(uow: UOWDep, email: str
) -> Annotated[SuccessResponseModel[SUserRole] | ErrorEnvelopeModel, Field(discriminator="status")]:
    """**Получить роль пользователя по email**"""
    return await UsersService().get_user_role(uow, email), 200

@router.post("/refresh", summary="Обновить access_token", status_code=status.HTTP_201_CREATED)
@api_exception_handler
async def refresh_token(uow: UOWDep, response: Response, request: Request
) -> Annotated[SuccessResponseModel[SUserTokens] | ErrorEnvelopeModel, Field(discriminator="status")]:
    """
    **Обновить access_token**
    """
    tokens = await UsersService().refresh_token(uow, response, request)
    return tokens, 201

@router.post("/logout", summary="Закончить сессию у пользователя", status_code=status.HTTP_200_OK)
@api_exception_handler
async def logout(
    uow: UOWDep, response: Response, request: Request, user: User = Depends(get_current_user)
) -> Annotated[SuccessResponseModel[SUserLogout] | ErrorEnvelopeModel, Field(discriminator="status")]:
    """
    **Закончить сессию у пользователя**
    """
    await UsersService().logout(uow, response, request)
    return {"result": "Logout success"}, 200

@router.get("/contractors", summary="Получить всех подрядчиков", status_code=status.HTTP_200_OK)
@api_exception_handler
async def get_contractors(uow: UOWDep, user: User = Depends(get_current_user)
) -> Annotated[SuccessResponseModel[list[SUsersContractor]] | ErrorEnvelopeModel, Field(discriminator="status")]:
    """**Получить всех подрядчиков**"""
    return await UsersService().get_contractors(uow), 200