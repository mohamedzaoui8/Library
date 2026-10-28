
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy import (
    Enum as SQLAlchemyEnum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.book import Book

FILE_FORMATS = ("pdf", "epub")

PROCESSING_STATUSES = (
    "pending",
    "processing",
    "completed",
    "failed",
)


class BookFile(Base):
    __tablename__ = "book_files"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    book_id: Mapped[int] = mapped_column(
        ForeignKey("books.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    file_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    original_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    file_path: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    file_format: Mapped[str] = mapped_column(
        SQLAlchemyEnum(
            *FILE_FORMATS,
            name="file_format_enum",
            native_enum=False,
            create_constraint=True,
        ),
        nullable=False,
    )

    file_size: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    processing_status: Mapped[str] = mapped_column(
        SQLAlchemyEnum(
            *PROCESSING_STATUSES,
            name="processing_status_enum",
            native_enum=False,
            create_constraint=True,
        ),
        default="pending",
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    book: Mapped["Book"] = relationship(
        "Book",
        back_populates="files",
    )
