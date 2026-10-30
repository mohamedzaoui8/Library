from pydantic import BaseModel, ConfigDict, Field

from app.schemas.book import BookResponse


class ReadingListItemCreate(BaseModel):
    book_id: int


class ReadingListItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    book_id: int
    book: BookResponse = Field(validation_alias="book_rel")



