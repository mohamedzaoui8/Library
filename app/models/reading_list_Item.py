from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.book import Book
from app.models.user import User


class ReadingListItem(Base):
    __tablename__ = "reading_list_items"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(nullable=False)
    book_id: Mapped[int] = mapped_column(nullable=False)
    user_rel: Mapped["User"] = relationship("User", back_populates="reading_list_items")
    book_rel: Mapped["Book"] = relationship("Book", back_populates="reading_list_items")