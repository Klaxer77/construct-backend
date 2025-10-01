import uuid
from datetime import UTC, datetime

from sqlalchemy import TIMESTAMP, UUID, Date, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.config.database import Base


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
    object_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("objects.id", ondelete="CASCADE")
    )
    category_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("categories_materials.id", ondelete="CASCADE")
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=lambda: datetime.now(UTC), server_default=func.now()
    )
    
class CategoriesMaterials(Base):
    """Таблица для категорий контроля материалов"""
    
    __tablename__ = "categories_materials"

    id: Mapped[uuid.UUID] = mapped_column(UUID, default=uuid.uuid4, primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID, ForeignKey("categories_materials.id", ondelete="CASCADE"), nullable=True
    )
    date_from: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True)
    )
    date_to: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True)
    )
    
    parent: Mapped["CategoriesMaterials"] = relationship(
        "CategoriesMaterials",
        remote_side=[id],
        back_populates="subcategories"
    )
    subcategories: Mapped[list["CategoriesMaterials"]] = relationship(
        "CategoriesMaterials",
        back_populates="parent"
    )