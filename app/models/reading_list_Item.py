from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
if TYPE_CHECKING:
    from app.models.book import Book
    from app.models.user import User


class ReadingListItem(Base):
    __tablename__ = "reading_list_items"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "book_id",
            name="uq_reading_list_user_book",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    book_id: Mapped[int] = mapped_column(
        ForeignKey("books.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_rel: Mapped["User"] = relationship("User", back_populates="reading_list_items")
    book_rel: Mapped["Book"] = relationship("Book", back_populates="reading_list_items")
