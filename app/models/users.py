import uuid
from datetime import UTC, datetime

from sqlalchemy import TIMESTAMP, UUID, BigInteger, Boolean, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.config.database import Base
from app.models.enums import UserRoleEnum, user_role_enum


class User(Base):
    """Таблица для пользователей"""
    
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID, default=uuid.uuid4, primary_key=True)
    using_id: Mapped[int] = mapped_column(BigInteger)
    avatar: Mapped[str] = mapped_column(String(255), nullable=True)
    fio: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    password: Mapped[str] = mapped_column(String(255))
    role: Mapped[UserRoleEnum] = mapped_column(user_role_enum)
    company_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("company.id", ondelete="SET NULL"), nullable=True)

    company: Mapped["Company"] = relationship("Company", backref="users") #noqa
    object_access = relationship("UserObjectAccess", backref="user", lazy="selectin")
    
class UserObjectAccess(Base):
    """Доступ пользователя к объекту"""

    __tablename__ = "user_object_access"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("users.id", ondelete="CASCADE")
    )
    object_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("objects.id", ondelete="CASCADE")
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    access_expires_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=lambda: datetime.now(UTC),
        server_default=func.now()
    )

class RefreshSession(Base):
    """Таблица для сессий пользователя"""

    __tablename__ = "refresh_session"

    id: Mapped[int] = mapped_column(UUID, default=uuid.uuid4, primary_key=True) 
    refresh_token: Mapped[uuid.UUID] = mapped_column(UUID)
    expires_in: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=lambda: datetime.now(UTC), server_default=func.now()
    )
    user_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("users.id", ondelete="CASCADE"))
    
    __table_args__ = (
        Index("ix_refresh_session_user_id_hash", "user_id", postgresql_using="hash"),
    )