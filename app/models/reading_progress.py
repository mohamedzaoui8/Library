from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.book import Book
from app.models.user import User

class ReadingProgress(Base):
    __tablename__ = "reading_progress"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(nullable=False)
    book_id: Mapped[int] = mapped_column(nullable=False)
    progress_percentage: Mapped[int] = mapped_column(nullable=False, default=0)
    user_rel: Mapped["User"] = relationship("User", back_populates="reading_progress")
    book_rel: Mapped["Book"] = relationship("Book", back_populates="reading_progress")
    