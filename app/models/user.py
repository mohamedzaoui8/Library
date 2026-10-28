from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.reading_list_Item import ReadingListItem
    from app.models.reading_progress import ReadingProgress


class UserRole(str, Enum):
    admin = "admin"
    member = "member"


class PaymentPlan(str, Enum):
    free = "free"
    premium = "premium"


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    username: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    role: Mapped[str] = mapped_column(String(50), default=UserRole.member.value)
    payment_plan: Mapped[str] = mapped_column(
        String(255), nullable=True, default=PaymentPlan.free.value
    )
    google_sub: Mapped[str | None] = mapped_column(
        String(255),
        unique=True,
        nullable=True,
    )
    email_verified: Mapped[bool] = mapped_column(default=False)
    email_verification_token_hash: Mapped[str | None] = mapped_column(
        String(64),
        unique=True,
        nullable=True,
    )

    email_verification_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    email_verification_sent_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    reading_list_items: Mapped[list["ReadingListItem"]] = relationship(
        "ReadingListItem",
        back_populates="user_rel",
    )
    reading_progress: Mapped[list["ReadingProgress"]] = relationship(
        "ReadingProgress",
        back_populates="user_rel",
    )
