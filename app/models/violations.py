import uuid
from datetime import UTC, datetime

from sqlalchemy import TIMESTAMP, UUID, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.config.database import Base
from app.models.enums import violation_status_enum


class ViolationPhoto(Base):
    """Фотографии для пункта нарушения"""

    __tablename__ = "violation_photos"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    violation_item_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("violations_item.id", ondelete="CASCADE")
    )
    file_path: Mapped[str] = mapped_column(String(255))

    violation_item = relationship("ViolationsItem", back_populates="photos")


class ViolationsItem(Base):
    """Подзамечание в общем замечании"""
    
    __tablename__ = "violations_item"

    id: Mapped[uuid.UUID] = mapped_column(UUID, default=uuid.uuid4, primary_key=True)
    violations: Mapped[str] = mapped_column(Text)
    name_regulatory_docx: Mapped[str] = mapped_column(Text)
    comment: Mapped[str] = mapped_column(Text, nullable=True)
    object_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("objects.id", ondelete="CASCADE")
    )
    date_violation: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))
    expiration_date: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))
    responsible_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    status: Mapped[str] = mapped_column(violation_status_enum)
    violations_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("violations.id", ondelete="CASCADE")
    )
    
    object = relationship("Objects", back_populates="violations_items")
    photos = relationship("ViolationPhoto", back_populates="violation_item")
    violation_container = relationship("Violations", back_populates="items")
    answer = relationship(
        "ViolationAnswer",
        back_populates="violation_item",
        uselist=False
    )
    
class ViolationAnswer(Base):
    """Ответ на нарушение"""

    __tablename__ = "violation_answers"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    violation_item_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("violations_item.id", ondelete="CASCADE"), unique=True
    )
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=lambda: datetime.now(UTC), server_default=func.now()
    )

    violation_item = relationship("ViolationsItem", back_populates="answer")
    files = relationship(
        "ViolationAnswerFile",
        back_populates="answer"
    )
    
class ViolationAnswerFile(Base):
    """Файлы, приложенные к ответу на нарушение"""

    __tablename__ = "violation_answer_files"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    answer_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("violation_answers.id", ondelete="CASCADE")
    )
    file_path: Mapped[str] = mapped_column(String(255))

    answer = relationship("ViolationAnswer", back_populates="files")


class Violations(Base):
    """Общее нарушение (контейнер для нескольких ViolationItem)"""
    
    __tablename__ = "violations"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID, default=uuid.uuid4, primary_key=True)
    date_violation: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))
    expiration_date: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))
    responsible_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    status: Mapped[str] = mapped_column(violation_status_enum)

    items = relationship("ViolationsItem", back_populates="violation_container")