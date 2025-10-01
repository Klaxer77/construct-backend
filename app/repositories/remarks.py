import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.objects import Objects
from app.models.remarks import RemarkAnswer, RemarkAnswerFile, RemarkPhoto, Remarks, RemarksItem
from app.repositories.base import SQLAlchemyRepository


class RemarkPhotoRepository(SQLAlchemyRepository):
    model = RemarkPhoto

    def __init__(self, session: AsyncSession):
        self.session = session
        
class RemarkAnswerRepository(SQLAlchemyRepository):
    model = RemarkAnswer

    def __init__(self, session: AsyncSession):
        self.session = session
        
class RemarkAnswerFileRepository(SQLAlchemyRepository):
    model = RemarkAnswerFile

    def __init__(self, session: AsyncSession):
        self.session = session
        
class RemarksItemRepository(SQLAlchemyRepository):
    model = RemarksItem

    def __init__(self, session: AsyncSession):
        self.session = session
        
class RemarksRepository(SQLAlchemyRepository):
    model = Remarks

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_remarks_detail(self, remark_id: uuid.UUID):
        stmt = (
            select(Remarks)
            .options(
                joinedload(Remarks.items)
                .joinedload(RemarksItem.photos),
                joinedload(Remarks.items)
                .joinedload(RemarksItem.object),
                joinedload(Remarks.items)
                .joinedload(RemarksItem.answer)
                .joinedload(RemarkAnswer.files)
            )
            .where(Remarks.id == remark_id)
        )
        result = await self.session.execute(stmt)
        remarks: Remarks | None = result.unique().scalar_one_or_none()

        if not remarks:
            return None

        object_name = None
        if remarks.items:
            first_item = remarks.items[0]
            if first_item.object:
                object_name = first_item.object.title
            else:
                object_name = str(first_item.object_id)

        return {
            "id": remarks.id,
            "date_remark": remarks.date_remark,
            "status": remarks.status,
            "expiration_date": remarks.expiration_date,
            "object_name": object_name,
            "remarks": [
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
                for item in remarks.items
            ]
        }
        
    async def get_all_remarks(self, object_id: uuid.UUID):
        stmt = (
            select(
                Remarks.id,
                Remarks.date_remark,
                Remarks.expiration_date,
                Remarks.responsible_user_id,
                Remarks.status,
                Objects.title.label("object_name")
            )
            .join(RemarksItem, RemarksItem.remarks_id == Remarks.id)
            .join(Objects, Objects.id == RemarksItem.object_id)
            .where(RemarksItem.object_id == object_id)
            .group_by(
                Remarks.id, 
                Remarks.date_remark, 
                Remarks.expiration_date, 
                Remarks.responsible_user_id, 
                Remarks.status, 
                Objects.title
                )
        )

        stmt = stmt.order_by(Remarks.date_remark.desc())

        result = await self.session.execute(stmt)
        return result.all()