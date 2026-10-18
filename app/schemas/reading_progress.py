from pydantic import BaseModel


class reading_progress_create(BaseModel):
    book_id: int
    page: int


class reading_progress_response(BaseModel):
    book_id: int
    page: int
