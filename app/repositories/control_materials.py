import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.control_materials import (
    ListOfWorks,
    Materials,
    ProgressWork,
    StageProgressWork,
    StageProgressWorkPhoto,
    StageProgressWorkRejection,
    StageProgressWorkRejectionPhoto,
)
from app.repositories.base import SQLAlchemyRepository


class MaterialsRepository(SQLAlchemyRepository):
    model = Materials

    def __init__(self, session: AsyncSession):
        self.session = session
        

class StageProgressWorkPhotoRepository(SQLAlchemyRepository):
    model = StageProgressWorkPhoto

    def __init__(self, session: AsyncSession):
        self.session = session

class StageProgressWorkRejectionPhotoRepository(SQLAlchemyRepository):
    model = StageProgressWorkRejectionPhoto

    def __init__(self, session: AsyncSession):
        self.session = session
        

class StageProgressWorkRejectionRepository(SQLAlchemyRepository):
    model = StageProgressWorkRejection

    def __init__(self, session: AsyncSession):
        self.session = session
        

class ListOfWorksRepository(SQLAlchemyRepository):
    model = ListOfWorks

    def __init__(self, session: AsyncSession):
        self.session = session
        
class StageProgressWorkRepository(SQLAlchemyRepository):
    model = StageProgressWork

    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def detail(self, stage_progress_work_id: uuid.UUID) -> dict:
        query = (
            select(StageProgressWork)
            .where(StageProgressWork.id == stage_progress_work_id)
            .options(
                selectinload(StageProgressWork.list_of_works)
                .selectinload(ListOfWorks.photos)
            )
        )

        result = await self.session.execute(query)
        stage: StageProgressWork | None = result.scalar_one_or_none()

        list_of_works_data = []
        for work in getattr(stage, "list_of_works", []):
            photos = [{"file_path": p.file_path} for p in getattr(work, "photos", [])]
            list_of_works_data.append({
                "id": str(work.id),
                "volume": work.volume,
                "status": work.status,
                "desc": work.desc,
                "created_at": work.created_at,
                "photos": photos
            })

        return {
            "id": stage.id,
            "percent": float(stage.percent or 0),
            "title": stage.title,
            "status_main": stage.status_main,
            "status_second": stage.status_second,
            "date_from": stage.date_from,
            "date_to": stage.date_to,
            "kpgz": stage.kpgz,
            "volume": stage.volume,
            "unit": stage.unit,
            "list_of_works": list_of_works_data
        }
        
class ProgressWorkRepository(SQLAlchemyRepository):
    model = ProgressWork

    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def progress(self, object_id: uuid.UUID) -> float:
        query = select(func.avg(ProgressWork.percent)).where(ProgressWork.object_id == object_id)
        result = await self.session.execute(query)
        avg_percent = result.scalar()

        return float(avg_percent or 0.0)
        
    async def list_work(self, object_id: uuid.UUID):
        """
        Получить все ходы работ по object_id с подгрузкой этапов.
        """
        query = (
            select(ProgressWork)
            .options(
                selectinload(ProgressWork.stages)
            )
            .where(ProgressWork.object_id == object_id)
            .order_by(ProgressWork.date_from)
        )

        result = await self.session.execute(query)
        return result.scalars().all()