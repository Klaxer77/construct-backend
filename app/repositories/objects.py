import uuid

from shapely import wkb
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.models.enums import ObjectTypeEnum, ObjectTypeFilter, UserRoleEnum
from app.models.objects import Acts, CheckList, CheckListDocument, Objects, ObjectsCategories
from app.models.users import User
from app.repositories.base import SQLAlchemyRepository
from app.schemas.objects import SObjectDetail
from app.schemas.users import SUserCurrentSubObject


class CheckListRepository(SQLAlchemyRepository):
    model = CheckList

    def __init__(self, session: AsyncSession):
        self.session = session


class ActsRepository(SQLAlchemyRepository):
    model = Acts

    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def get_check_list_detail(self, object_id: uuid.UUID) -> CheckList | None:
        stmt = (
            select(CheckList)
            .options(
                selectinload(CheckList.documents),
                joinedload(CheckList.object)
                    .joinedload(Objects.responsible_user),
                joinedload(CheckList.object)
                    .joinedload(Objects.contractor)
            )
            .where(CheckList.object_id == object_id)
        )

        result = await self.session.execute(stmt)
        return result.scalars().first()
        
class CheckListDocumentRepository(SQLAlchemyRepository):
    model = CheckListDocument

    def __init__(self, session: AsyncSession):
        self.session = session

class ObjectsRepository(SQLAlchemyRepository):
    model = Objects

    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def get_all_objects_by_filter(
        self, 
        filter_by: ObjectTypeFilter, 
        company_id: uuid.UUID,
        user: User
        ):
        stmt = (
            select(Objects)
            .options(
                joinedload(Objects.remarks_items),
                joinedload(Objects.act),
                joinedload(Objects.check_list),
                joinedload(Objects.responsible_user),
                selectinload(Objects.nfc_items)
            )
        )
        
        if user.role != UserRoleEnum.INSPECTIION:
            if user.role == UserRoleEnum.CONTRACTOR:
                stmt = stmt.where(
                    Objects.contractor_id == user.company_id
                )
            else:
                stmt = stmt.where(Objects.company_id == company_id)

        if filter_by == ObjectTypeFilter.ACTIVE:
            stmt = stmt.where(Objects.object_type == ObjectTypeFilter.ACTIVE)
        elif filter_by == ObjectTypeFilter.NOT_ACTIVE:
            stmt = stmt.where(Objects.object_type == ObjectTypeFilter.NOT_ACTIVE)
        elif filter_by == ObjectTypeFilter.AGREEMENT:
            stmt = stmt.where(Objects.object_type == ObjectTypeFilter.AGREEMENT)
        elif filter_by == ObjectTypeFilter.ACT_OPENING:
            stmt = stmt.where(Objects.object_type == ObjectTypeFilter.ACT_OPENING)

        result = await self.session.execute(stmt)
        return result.unique().scalars().all()
        
    async def get_object_detail(self, object_id: uuid.UUID):
        query = (
            select(
                Objects.id,
                Objects.using_id,
                Objects.status,
                Objects.object_type,
                Objects.created_at,
                Objects.updated_at,
                Objects.general_info,
                Objects.title,
                Objects.city,
                Objects.date_delivery_verification,
                Objects.start_date,
                Objects.geom,
                User.id.label("user_id"),
                User.using_id.label("user_using_id"),
                User.avatar,
                User.email,
                User.fio,
                User.role
            )
            .join(User, Objects.responsible_user_id == User.id, isouter=True)
            .where(Objects.id == object_id)
        )

        result = await self.session.execute(query)
        row = result.mappings().first()
        if not row:
            return None

        coords = None
        if row["geom"]:
            geom_wkb = bytes(row["geom"].data) if hasattr(row["geom"], "data") else row["geom"]
            shape = wkb.loads(geom_wkb)

            if shape.geom_type == "Polygon":
                coords = [tuple(coord) for coord in shape.exterior.coords]
            elif shape.geom_type == "MultiPolygon":
                coords = [
                    [tuple(coord) for coord in poly.exterior.coords]
                    for poly in shape.geoms
                ]

        return SObjectDetail(
            id=row["id"],
            using_id=row["using_id"],
            status=row["status"],
            object_type=row["object_type"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            general_info=row["general_info"],
            title=row["title"],
            city=row["city"],
            date_delivery_verification=row["date_delivery_verification"],
            start_date=row["start_date"],
            coords=coords,
            responsible_user=(
                SUserCurrentSubObject(
                    id=row["user_id"],
                    using_id=row["user_using_id"],
                    avatar=row["avatar"],
                    email=row["email"],
                    fio=row["fio"],
                    role=row["role"],
                )
                if row["user_id"]
                else None
            )
        )
        
    async def count_objects(
        self, 
        category_id: uuid.UUID | None, 
        filter_by: ObjectTypeEnum,
        company_id: uuid.UUID,
        user: User
        ) -> int:
        query = select(func.count()).select_from(Objects)
        
        if user.role != UserRoleEnum.INSPECTIION:
            if user.role == UserRoleEnum.CONTRACTOR:
                query.where(
                    Objects.contractor_id == user.company_id
                )
            else:
                query = query.where(Objects.company_id == company_id)
        
        if category_id:
            query = query.where(Objects.category_id==category_id)
            
        if filter_by == ObjectTypeFilter.ACT_OPENING:
            query = query.where(Objects.object_type == filter_by.value)
        elif filter_by == ObjectTypeFilter.ACTIVE:
            query = query.where(Objects.object_type == filter_by.value)
        elif filter_by == ObjectTypeFilter.NOT_ACTIVE:
            query = query.where(Objects.object_type == filter_by.value)
        elif filter_by == ObjectTypeFilter.AGREEMENT:
            query = query.where(Objects.object_type == filter_by.value)
            
        result = await self.session.execute(query)
        return result.scalar_one()
        
    async def get_status_projects(self, company_id: uuid.UUID, user: User):
        stmt = (
            select(
                Objects.id,
                Objects.title,
                Objects.city,
                Objects.updated_at,
                Objects.status,
                User.fio.label("responsible_fio"),
                Objects.geom
            )
            .join(User, Objects.responsible_user_id == User.id, isouter=True)
        )
        
        if user.role != UserRoleEnum.INSPECTIION:
            if user.role == UserRoleEnum.CONTRACTOR:
                stmt = stmt.where(
                    Objects.contractor_id == user.company_id
                ) 
            else:
                stmt = stmt.where(Objects.company_id == company_id)

        result = await self.session.execute(stmt)
        rows = result.all()

        projects = []
        for row in rows:
            coords = None
            if row.geom:
                geom_wkb = bytes(row.geom.data) if hasattr(row.geom, "desc") else row.geom
                shape = wkb.loads(geom_wkb)

                if shape.geom_type == "Polygon":
                    # просто список кортежей
                    coords = [tuple(pt) for pt in shape.exterior.coords]
                elif shape.geom_type == "MultiPolygon":
                    # список списков кортежей
                    coords = [[tuple(pt) for pt in poly.exterior.coords] for poly in shape.geoms]

            projects.append({
                "id": row.id,
                "title": row.title,
                "city": row.city,
                "status": row.status,
                "updated_at": row.updated_at,
                "responsible_user": {"fio": row.responsible_fio} if row.responsible_fio else None,
                "coords": coords
            })
        
        return projects
        
class ObjectsCategoriesRepository(SQLAlchemyRepository):
    model = ObjectsCategories

    def __init__(self, session: AsyncSession):
        self.session = session