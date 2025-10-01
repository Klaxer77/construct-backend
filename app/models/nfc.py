import uuid
from datetime import UTC, datetime

from sqlalchemy import TIMESTAMP, UUID, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.config.database import Base


class ObjectNFC(Base):
    """NFC-метки, привязанные к объекту"""

    __tablename__ = "object_nfc"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    object_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("objects.id", ondelete="CASCADE")
    )
    nfc_uid: Mapped[str] = mapped_column(String(255), unique=True)
    label: Mapped[str] = mapped_column(String(10))
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=lambda: datetime.now(UTC), server_default=func.now()
        )
    
    
class HistoryObjectNFC(Base):
    """История привязок NFC меток к объекту"""

    __tablename__ = "history_object_nfc"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    nfc_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("object_nfc.id", ondelete="CASCADE")
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID, ForeignKey("users.id", ondelete="CASCADE")
        )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=lambda: datetime.now(UTC), server_default=func.now()
        )