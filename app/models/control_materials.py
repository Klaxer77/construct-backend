import uuid
from datetime import UTC, datetime

from sqlalchemy import TIMESTAMP, UUID, Date, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.config.database import Base
from app.models.enums import (
    list_of_works_status_enum,
    stage_progress_work_main_status_enum,
    stage_progress_work_second_status_enum,
)


class Materials(Base):
    """Таблица для контроля материалов"""
    
    __tablename__ = "materials"

    id: Mapped[uuid.UUID] = mapped_column(UUID, default=uuid.uuid4, primary_key=True)
    sender: Mapped[str] = mapped_column(Text)
    date: Mapped[str] = mapped_column(Date)
    request_number: Mapped[str] = mapped_column(Text)
    receiver: Mapped[str] = mapped_column(Text)
    item_name: Mapped[str] = mapped_column(Text)
    size: Mapped[str] = mapped_column(Text)
    quantity: Mapped[str] = mapped_column(Text)
    net_weight: Mapped[str] = mapped_column(Text)
    gross_weight: Mapped[str] = mapped_column(Text)
    volume: Mapped[str] = mapped_column(Text)
    carrier: Mapped[str] = mapped_column(Text)
    vehicle: Mapped[str] = mapped_column(Text)
    stage_progress_work_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("stage_progress_work.id", ondelete="CASCADE")
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=lambda: datetime.now(UTC), server_default=func.now()
    )
    
class StageProgressWorkPhoto(Base):
    """Фотографии для хода работ"""

    __tablename__ = "stage_progress_work_photos"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    list_of_works_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("list_of_works.id", ondelete="CASCADE")
    )
    file_path: Mapped[str] = mapped_column(String(255))
    
class StageProgressWorkRejectionPhoto(Base):
    """Фото, прикрепленные к отказу этапа"""
    
    __tablename__ = "stage_progress_work_rejection_photos"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    rejection_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("stage_progress_work_rejections.id", ondelete="CASCADE")
    )
    file_path: Mapped[str] = mapped_column(String(255))
    
class StageProgressWorkRejection(Base):
    """Отказы этапа работы с фото и описанием"""
    
    __tablename__ = "stage_progress_work_rejections"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    stage_progress_work_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("stage_progress_work.id", ondelete="CASCADE")
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=lambda: datetime.now(UTC), server_default=func.now()
    )
    
class ListOfWorks(Base):
    """Таблица для перечьня работ"""

    __tablename__ = "list_of_works"
    id: Mapped[uuid.UUID] = mapped_column(UUID, default=uuid.uuid4, primary_key=True)
    volume: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(list_of_works_status_enum)
    desc: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=lambda: datetime.now(UTC), server_default=func.now()
    )
    stage_progress_work_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("stage_progress_work.id", ondelete="CASCADE")
    )
    
    photos: Mapped[list["StageProgressWorkPhoto"]] = relationship(
        "StageProgressWorkPhoto", backref="list_of_works", lazy="selectin"
    )

class StageProgressWork(Base):
    """Таблица для этапов хода работ"""
    
    __tablename__ = "stage_progress_work"

    id: Mapped[uuid.UUID] = mapped_column(UUID, default=uuid.uuid4, primary_key=True)  
    percent: Mapped[float] = mapped_column(Numeric(5, 4)) 
    title: Mapped[str] = mapped_column(String(255))
    status_main: Mapped[str] = mapped_column(stage_progress_work_main_status_enum)
    status_second: Mapped[str] = mapped_column(stage_progress_work_second_status_enum)
    date_from: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True)
    )
    date_to: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True)
    )
    kpgz: Mapped[str] = mapped_column(String(255))
    volume: Mapped[int] = mapped_column(Integer)
    unit: Mapped[str] = mapped_column(String(255))
    progress_work_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("progress_work.id", ondelete="CASCADE")
    )
    
    progress_work: Mapped["ProgressWork"] = relationship(
        "ProgressWork", back_populates="stages", lazy="joined"
    )

    list_of_works: Mapped[list["ListOfWorks"]] = relationship(
        "ListOfWorks", backref="stage_progress_work", cascade="all, delete-orphan", lazy="selectin"
    )

    rejections: Mapped[list["StageProgressWorkRejection"]] = relationship(
        "StageProgressWorkRejection", backref="stage_progress_work", cascade="all, delete-orphan", lazy="selectin"
    )
    
class ProgressWork(Base):
    """Таблица для хода работ"""
    
    __tablename__ = "progress_work"

    id: Mapped[uuid.UUID] = mapped_column(UUID, default=uuid.uuid4, primary_key=True)
    percent: Mapped[float] = mapped_column(Numeric(5, 4))
    title: Mapped[str] = mapped_column(String(255))
    date_from: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True)
    )
    date_to: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True)
    )
    object_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("objects.id", ondelete="CASCADE")
    )
    
    stages: Mapped[list["StageProgressWork"]] = relationship(
        back_populates="progress_work"
    )