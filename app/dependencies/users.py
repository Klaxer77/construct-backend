import uuid
from datetime import UTC, datetime, timedelta

from fastapi import Depends, Request
from jose import ExpiredSignatureError, JWTError, jwt
from passlib.context import CryptContext

from app.config.main import settings
from app.dependencies.unitofwork import UOWDep
from app.exceptions.forbidden import PermissionAccessDenied
from app.exceptions.users import (
    IncorrectPasswordExc,
    IncorrectTokenFormatExc,
    TokenExpiredExc,
    TokenNotFoundExc,
    UserIsNotPresentExc,
)
from app.models.enums import UserRoleEnum
from app.models.users import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def get_token(request: Request) -> str:
    try:
        token = request.cookies.get("access_token")
        if not token:
            raise TokenNotFoundExc
        return token

    except TokenNotFoundExc:
        raise TokenNotFoundExc


async def get_current_user(uow: UOWDep, token: str = Depends(get_token)) -> User:
    try:
        async with uow:
            try:
                payload = jwt.decode(token, settings.SECRET_KEY, settings.ALGORITHM)
            except ExpiredSignatureError:
                raise TokenExpiredExc
            except JWTError:
                raise IncorrectTokenFormatExc
            user_id: str = payload.get("sub")
            if not user_id:
                raise UserIsNotPresentExc
            user: User = await uow.users.find_one_or_none(id=uuid.UUID(user_id))
            if not user:
                raise UserIsNotPresentExc
            uow.session.expunge(user)
            return user

    except TokenExpiredExc:
        raise TokenExpiredExc
    except IncorrectTokenFormatExc:
        raise IncorrectTokenFormatExc
    except UserIsNotPresentExc:
        raise UserIsNotPresentExc


def create_access_token(user_id: uuid.UUID) -> str:
    to_encode = {
        "sub": str(user_id),
        "exp": datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token() -> str:
    return uuid.uuid4()


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


async def get_current_construction_control_user(user: User = Depends(get_current_user)) -> User:
    if user.role != UserRoleEnum.CONSTRUCTION_CONTROL:
        raise PermissionAccessDenied
    return user


async def get_current_contractor_user(user: User = Depends(get_current_user)) -> User:
    if user.role != UserRoleEnum.CONTRACTOR:
        raise PermissionAccessDenied
    return user


async def get_current_inspection_user(user: User = Depends(get_current_user)) -> User:
    if user.role != UserRoleEnum.INSPECTIION:
        raise PermissionAccessDenied
    return user

async def authenticate_user(uow: UOWDep, user: User, password: str):
    try:
        if not (user and verify_password(password, user.password)):
            raise IncorrectPasswordExc
        uow.session.expunge(user)
        return user

    except IncorrectPasswordExc:
        raise IncorrectPasswordExc
