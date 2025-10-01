from datetime import UTC, datetime, timedelta

from fastapi import Request, Response

from app.config.main import settings
from app.dependencies.unitofwork import UnitOfWork
from app.dependencies.users import authenticate_user, create_access_token, create_refresh_token
from app.exceptions.users import IncorrectEmailExc, InvalidTokenExc, TokenExpiredExc, UserNotFoundExc
from app.models.users import RefreshSession, User
from app.schemas.users import SUserCurrent, SUserLogin, SUserRole, SUsersContractor, SUserTokens


class UsersService:
    
    async def get_current_user(self, uow: UnitOfWork, user: User) -> SUserCurrent:
        async with uow:
            current_user = await uow.users.current(user)
            return SUserCurrent.model_validate(current_user)
    
    async def get_contractors(self, uow: UnitOfWork) -> list[SUsersContractor]:
        async with uow:
            contractors = await uow.users.find_all_contractors()
            return [SUsersContractor.model_validate(contractor) for contractor in contractors]
    
    async def get_user_role(self, uow: UnitOfWork, email: str) -> SUserRole:
        async with uow:
            check_user: User | None = await uow.users.find_one_or_none(email=email)
            if not check_user:
                raise UserNotFoundExc
            return SUserRole.model_validate({"role": check_user.role})

    async def login(self, uow: UnitOfWork, user_data: SUserLogin, response: Response) -> User:
        async with uow:
            find_user: User | None = await uow.users.find_one_or_none(email=user_data.email)
            if not find_user:
                raise IncorrectEmailExc

            user: User = await authenticate_user(uow, find_user, user_data.password)

            access_token = create_access_token(user_id=user.id)
            refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
            refresh_token = create_refresh_token()

            await uow.refresh_session.insert_by_data(
                {
                    "refresh_token": refresh_token,
                    "expires_in": refresh_token_expires.total_seconds(),
                    "user_id": user.id,
                }
            )

            response.set_cookie(
                "access_token",
                access_token,
                max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                samesite=settings.COOKIE_SAMESITE,
                secure=settings.COOKIE_SECURE,
                httponly=True
            )

            response.set_cookie(
                "refresh_token",
                refresh_token,
                max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 30 * 24 * 60,
                samesite=settings.COOKIE_SAMESITE,
                secure=settings.COOKIE_SECURE,
                httponly=True
            )
            
            user_with_access_object = await uow.users.current(user)
            await uow.commit()
            return SUserCurrent.model_validate(user_with_access_object)

    async def refresh_token(self, uow: UnitOfWork, response: Response, request: Request) -> SUserTokens:
        async with uow:
            refresh_session: RefreshSession | None = await uow.refresh_session.find_one_or_none(
                refresh_token=request.cookies.get("refresh_token")
            )

            if refresh_session is None:
                raise InvalidTokenExc
            
            if datetime.now(UTC) >= refresh_session.created_at + timedelta(
                seconds=refresh_session.expires_in
            ):
                await uow.refresh_session.delete_by_filter(id=refresh_session.id)
                await uow.commit()
                raise TokenExpiredExc

            user: User | None = await uow.users.find_one_or_none(id=refresh_session.user_id)
            if not user:
                raise InvalidTokenExc
            
            access_token = create_access_token(user.id)
            refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
            refresh_token = create_refresh_token()

            await uow.refresh_session.update_session(
                refresh_session_id=refresh_session.id,
                refresh_token=refresh_token,
                expires_in=refresh_token_expires.total_seconds(),
            )

            response.set_cookie(
                "access_token",
                access_token,
                max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                samesite=settings.COOKIE_SAMESITE,
                secure=settings.COOKIE_SECURE,
                httponly=True
            )
            response.set_cookie(
                "refresh_token",
                refresh_token,
                max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 30 * 24 * 60,
                samesite=settings.COOKIE_SAMESITE,
                secure=settings.COOKIE_SECURE,
                httponly=True
            )
            await uow.commit()
            return SUserTokens(access_token=access_token, refresh_token=refresh_token)

    async def logout(self, uow: UnitOfWork, response: Response, request: Request) -> None:
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")

        async with uow:
            refresh_session: RefreshSession = await uow.refresh_session.find_one_or_none(
                refresh_token=request.cookies.get("refresh_token")
            )
            if refresh_session:
                await uow.refresh_session.delete_by_filter(id=refresh_session.id)
                await uow.commit()
