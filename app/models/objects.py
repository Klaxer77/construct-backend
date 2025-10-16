import uuid
from datetime import UTC, datetime

from geoalchemy2 import Geometry
from sqlalchemy import TIMESTAMP, UUID, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.config.database import Base
from app.models.enums import (
    act_status_enum,
    check_list_status_enum,
    document_status_enum,
    object_statuses_enum,
    object_type_enum,
)


class Objects(Base):
    """Таблица для строительных объектов"""
    
    __tablename__ = "objects"

    id: Mapped[int] = mapped_column(UUID, default=uuid.uuid4, primary_key=True)
    using_id: Mapped[str] = mapped_column(String(255), unique=True)
    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("company.id", ondelete="CASCADE")
        )
    general_info: Mapped[str] = mapped_column(Text)
    title: Mapped[str] = mapped_column(String(255))
    city: Mapped[str] = mapped_column(String(255))
    responsible_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
        )
    contractor_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID, ForeignKey("company.id", ondelete="CASCADE"), nullable=True
    )
    category_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("objects_categories.id", ondelete="CASCADE")
        )
    date_delivery_verification: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True)
        )
    start_date: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True)
        )
    status: Mapped[str] = mapped_column(object_statuses_enum)
    object_type: Mapped[str] = mapped_column(object_type_enum)
    geom: Mapped[str] = mapped_column(
        Geometry(srid=4326)
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=lambda: datetime.now(UTC), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), 
        default=lambda: datetime.now(UTC), 
        onupdate=lambda: datetime.now(UTC), 
        server_default=func.now()
    )
    
    nfc_items = relationship("ObjectNFC", backref="object", lazy="selectin")
    responsible_user = relationship("User", lazy="joined")
    act = relationship("Acts", backref="object", uselist=False, lazy="joined")
    check_list = relationship("CheckList", backref="object", uselist=False, lazy="joined")
    remarks_items = relationship("RemarksItem", back_populates="object")
    violations_items = relationship("ViolationsItem", back_populates="object")
    contractor = relationship("Company", foreign_keys=[contractor_id], lazy="selectin")
    user_access = relationship("UserObjectAccess", backref="object", lazy="selectin")

    
    @property
    def is_nfc(self) -> bool:
        return bool(self.nfc_items)

class Acts(Base):
    """Таблица для строительных актов"""
    
    __tablename__ = "acts"
    
    id: Mapped[int] = mapped_column(UUID, default=uuid.uuid4, primary_key=True)
    file_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(act_status_enum)
    object_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("objects.id", ondelete="CASCADE"), unique=True
    )
    
class CheckList(Base):
    """Таблица для чек листа"""
    
    __tablename__ = "checklist"
    
    id: Mapped[int] = mapped_column(UUID, default=uuid.uuid4, primary_key=True)
    status: Mapped[str] = mapped_column(check_list_status_enum)
    object_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("objects.id", ondelete="CASCADE"), unique=True
    )
    date_verification: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
        )
    
    documents = relationship("CheckListDocument", backref="act", lazy="selectin")
    
class CheckListDocument(Base):
    """Пункты документов в строительных актах"""

    __tablename__ = "checklist_documents"

    id: Mapped[int] = mapped_column(UUID, default=uuid.uuid4, primary_key=True)
    checklist_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("checklist.id", ondelete="CASCADE")
    )
    # Номер пункта (например "1.1", "2.7")
    code: Mapped[str] = mapped_column(String(10))
    title: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(document_status_enum)
    description: Mapped[str | None] = mapped_column(Text, default="По требованию", nullable=True)


class ObjectsCategories(Base):
    """Таблица для категорий строительных объектов"""
    
    __tablename__ = "objects_categories"

    id: Mapped[int] = mapped_column(UUID, default=uuid.uuid4, primary_key=True)
    title: Mapped[str] = mapped_column(String(255))