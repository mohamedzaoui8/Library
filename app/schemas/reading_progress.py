from pydantic import BaseModel, ConfigDict, Field


class ReadingProgressUpdate(BaseModel):
    progress_percentage: int = Field(ge=0, le=100)


class ReadingProgressResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    book_id: int
    progress_percentage: int