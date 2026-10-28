from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.author import Author
from app.models.category import Category

if TYPE_CHECKING:
    from app.models.book_file import BookFile
    from app.models.reading_list_Item import ReadingListItem
    from app.models.reading_progress import ReadingProgress


class Book(Base):
    __tablename__ = "books"
    id: Mapped[int] = mapped_column( index=True ,primary_key=True)
    title: Mapped[str] = mapped_column(String(250), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id"), nullable=False,)
    author_rel: Mapped["Author"] = relationship("Author", back_populates="book_rel")
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False)
    category_rel: Mapped["Category"] = relationship("Category", back_populates="books_rel")
    files: Mapped[list["BookFile"]] = relationship(
        "BookFile",
        back_populates="book",
    )
    reading_list_items: Mapped[list["ReadingListItem"]] = relationship(
        "ReadingListItem",
        back_populates="book_rel",
    )
    reading_progress: Mapped[list["ReadingProgress"]] = relationship(
        "ReadingProgress",
        back_populates="book_rel",
    )
