import uuid

from sqlalchemy import UUID, String
from sqlalchemy.orm import Mapped, mapped_column

from app.config.database import Base


class Company(Base):
    """Таблица для компании"""
    
    __tablename__ = "company"

    id: Mapped[uuid.UUID] = mapped_column(UUID, default=uuid.uuid4, primary_key=True)
    title: Mapped[str] = mapped_column(String(255))