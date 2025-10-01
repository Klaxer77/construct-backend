import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.objects import Objects
from app.models.violations import ViolationAnswer, ViolationAnswerFile, ViolationPhoto, Violations, ViolationsItem
from app.repositories.base import SQLAlchemyRepository


class ViolationPhotoRepository(SQLAlchemyRepository):
    model = ViolationPhoto

    def __init__(self, session: AsyncSession):
        self.session = session
        
class ViolationAnswerRepository(SQLAlchemyRepository):
    model = ViolationAnswer

    def __init__(self, session: AsyncSession):
        self.session = session
        
class ViolationAnswerFileRepository(SQLAlchemyRepository):
    model = ViolationAnswerFile

    def __init__(self, session: AsyncSession):
        self.session = session
        
class ViolationsItemRepository(SQLAlchemyRepository):
    model = ViolationsItem

    def __init__(self, session: AsyncSession):
        self.session = session
        
class ViolationsRepository(SQLAlchemyRepository):
    model = Violations

    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_violations_detail(self, violation_id: uuid.UUID):
        stmt = (
            select(Violations)
            .options(
                joinedload(Violations.items)
                .joinedload(ViolationsItem.photos),
                joinedload(Violations.items)
                .joinedload(ViolationsItem.object),
                joinedload(Violations.items)
                .joinedload(ViolationsItem.answer)
                .joinedload(ViolationAnswer.files)
            )
            .where(Violations.id == violation_id)
        )
        result = await self.session.execute(stmt)
        violations: Violations | None = result.unique().scalar_one_or_none()

        if not violations:
            return None

        object_name = None
        if violations.items:
            first_item = violations.items[0]
            if first_item.object:
                object_name = first_item.object.title
            else:
                object_name = str(first_item.object_id)

        return {
            "id": violations.id,
            "date_violation": violations.date_violation,
            "status": violations.status,
            "expiration_date": violations.expiration_date,
            "object_name": object_name,
            "violations": [
                {
                    "id": item.id,
                    "violations": item.violations,
                    "status": item.status,
                    "name_regulatory_docx": item.name_regulatory_docx,
                    "comment": item.comment,
                    "expiration_date": item.expiration_date,
                    "photos": [{"file_path": photo.file_path} for photo in item.photos],
                    "answer": (
                        {
                            "id": item.answer.id,
                            "comment": item.answer.comment,
                            "created_at": item.answer.created_at,
                            "files": [
                                {"file_path": f.file_path} for f in item.answer.files
                            ]
                        }
                        if item.answer else None
                    )
                }
                for item in violations.items
            ]
        }
        
    async def get_all_violations(self, object_id: uuid.UUID):
        stmt = (
            select(
                Violations.id,
                Violations.date_violation,
                Violations.expiration_date,
                Violations.responsible_user_id,
                Violations.status,
                Objects.title.label("object_name")
            )
            .join(ViolationsItem, ViolationsItem.violations_id == Violations.id)
            .join(Objects, Objects.id == ViolationsItem.object_id)
            .where(ViolationsItem.object_id == object_id)
            .group_by(
                Violations.id, 
                Violations.date_violation, 
                Violations.expiration_date, 
                Violations.responsible_user_id, 
                Violations.status, 
                Objects.title
                )
        )

        stmt = stmt.order_by(Violations.date_violation.desc())

        result = await self.session.execute(stmt)
        return result.all()