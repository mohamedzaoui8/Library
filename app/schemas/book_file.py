from datetime import datetime

from pydantic import BaseModel, ConfigDict


class BookFileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    book_id: int
    original_name: str
    file_format: str
    file_size: int
    processing_status: str
    created_at: datetime