import uuid

from geoalchemy2 import Geography, Geometry
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.enums import UserRoleEnum
from app.models.objects import Objects
from app.models.users import RefreshSession, User, UserObjectAccess
from app.repositories.base import SQLAlchemyRepository


class UserObjectAccessRepository(SQLAlchemyRepository):
    model = UserObjectAccess

    def __init__(self, session: AsyncSession):
        self.session = session

class UsersRepository(SQLAlchemyRepository):
    model = User

    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def current(self, user: User):
        stmt = (
            select(User)
            .options(joinedload(User.object_access))
            .where(User.id == user.id)
        )

        result = await self.session.execute(stmt)
        return result.unique().scalar_one()
        
    async def find_all_contractors(self):
        query = (
            select(User)
            .options(joinedload(User.company))
            .where(User.role == UserRoleEnum.CONTRACTOR)
        )
        result = await self.session.execute(query)
        return result.scalars().all()
        
    async def get_users_by_ids(self, user_ids: list[uuid.UUID]):
        if not user_ids:
            return []

        query = select(self.model).where(self.model.id.in_(user_ids))
        result = await self.session.execute(query)
        return result.scalars().all()
        
    async def validate_coords(self, object_id: str, lat: float, lon: float) -> bool:
        stmt = (
            select(
                func.ST_Contains(
                    func.cast(func.ST_Buffer(func.cast(Objects.geom, Geography), 200), Geometry),
                    func.ST_SetSRID(func.ST_MakePoint(lon, lat), 4326)
                ).label("allowed")
            )
            .where(Objects.id == object_id)
        )
        # допускаем погрешность в 200м
        result = await self.session.execute(stmt)
        allowed = result.scalar()
        return bool(allowed)


class RefreshSessionRepository(SQLAlchemyRepository):
    model = RefreshSession

    def __init__(self, session: AsyncSession):
        self.session = session

    async def update_session(self, refresh_session_id: uuid.UUID, refresh_token: uuid.UUID, expires_in: int) -> None:
        """Обновить сессию"""
        query = (
            update(RefreshSession)
            .where(RefreshSession.id == refresh_session_id)
            .values(refresh_token=refresh_token, expires_in=expires_in)
        )
        await self.session.execute(query)