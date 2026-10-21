from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Book(Base):
    __tablename__ = "books"
    id: Mapped[int] = mapped_column( index=True ,primary_key=True)
    title: Mapped[str] = mapped_column(String(250), nullable=False)
    author: Mapped[str | None] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=False)
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id"), nullable=False,)
    author_rel: Mapped["Author"] = relationship("Author", back_populates="book_rel")
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False)
    category_rel: Mapped["Category"] = relationship("Category", back_populates="book_rel") 