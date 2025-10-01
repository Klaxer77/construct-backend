import uuid
from datetime import UTC, datetime

from sqlalchemy import TIMESTAMP, UUID, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.config.database import Base
from app.models.enums import remark_status_enum


class RemarkPhoto(Base):
    """Фотографии для пункта замечания"""

    __tablename__ = "remark_photos"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    remark_item_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("remarks_item.id", ondelete="CASCADE")
    )
    file_path: Mapped[str] = mapped_column(String(255))

    remark_item = relationship("RemarksItem", back_populates="photos")


class RemarksItem(Base):
    """Подзамечание в общем замечании"""
    
    __tablename__ = "remarks_item"

    id: Mapped[uuid.UUID] = mapped_column(UUID, default=uuid.uuid4, primary_key=True)
    violations: Mapped[str] = mapped_column(Text)
    name_regulatory_docx: Mapped[str] = mapped_column(Text)
    comment: Mapped[str] = mapped_column(Text, nullable=True)
    object_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("objects.id", ondelete="CASCADE")
    )
    date_remark: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))
    expiration_date: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))
    responsible_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    status: Mapped[str] = mapped_column(remark_status_enum)
    remarks_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("remarks.id", ondelete="CASCADE")
    )
    
    object = relationship("Objects", back_populates="remarks_items")
    photos = relationship("RemarkPhoto", back_populates="remark_item")
    remarks = relationship("Remarks", back_populates="items")
    answer = relationship(
        "RemarkAnswer",
        back_populates="remark_item",
        uselist=False
    )
    
class RemarkAnswer(Base):
    """Ответ на подзамечание"""

    __tablename__ = "remark_answers"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    remark_item_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("remarks_item.id", ondelete="CASCADE"), unique=True
    )
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=lambda: datetime.now(UTC), server_default=func.now()
    )

    remark_item = relationship("RemarksItem", back_populates="answer")
    files = relationship("RemarkAnswerFile", back_populates="answer", cascade="all, delete-orphan")
    

class RemarkAnswerFile(Base):
    """Файлы, приложенные к ответу"""

    __tablename__ = "remark_answer_files"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    answer_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("remark_answers.id", ondelete="CASCADE")
    )
    file_path: Mapped[str] = mapped_column(String(255))

    answer = relationship("RemarkAnswer", back_populates="files")


class Remarks(Base):
    """Общее замечание (контейнер для нескольких RemarkItem)"""
    
    __tablename__ = "remarks"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID, default=uuid.uuid4, primary_key=True)
    date_remark: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))
    expiration_date: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))
    responsible_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    status: Mapped[str] = mapped_column(remark_status_enum)

    items = relationship("RemarksItem", back_populates="remarks")