import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.nfc import HistoryObjectNFC, ObjectNFC
from app.models.objects import Objects
from app.models.users import User
from app.repositories.base import SQLAlchemyRepository


class ObjectNFCRepository(SQLAlchemyRepository):
    model = ObjectNFC

    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def history_all(self, user: User):
        stmt = (
            select(
                Objects.using_id,
                Objects.title,
                func.date(HistoryObjectNFC.created_at).label("scan_date"),
                ObjectNFC.label,
                HistoryObjectNFC.created_at.label("scanned_at"),
            )
            .join(ObjectNFC, ObjectNFC.id == HistoryObjectNFC.nfc_id)
            .join(Objects, Objects.id == ObjectNFC.object_id)
            .where(HistoryObjectNFC.user_id == user.id)
            .order_by(HistoryObjectNFC.created_at.desc())
        )

        result = await self.session.execute(stmt)
        return result.mappings().all()
        
    async def history(self, user: User, object_id: uuid.UUID):
        stmt = (
            select(
                Objects.using_id,
                Objects.title,
                func.date(HistoryObjectNFC.created_at).label("scan_date"),
                ObjectNFC.label,
                HistoryObjectNFC.created_at.label("scanned_at"),
            )
            .join(ObjectNFC, ObjectNFC.id == HistoryObjectNFC.nfc_id)
            .join(Objects, Objects.id == ObjectNFC.object_id)
            .where(HistoryObjectNFC.user_id == user.id, ObjectNFC.object_id == object_id)
            .order_by(HistoryObjectNFC.created_at.desc())
        )

        result = await self.session.execute(stmt)
        return result.mappings().all()
        
class HistoryObjectNFCRepository(SQLAlchemyRepository):
    model = HistoryObjectNFC

    def __init__(self, session: AsyncSession):
        self.session = session