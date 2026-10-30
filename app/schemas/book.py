from pydantic import BaseModel, ConfigDict, Field

from app.schemas.author import AuthorBrief
from app.schemas.category import CategoryBrief


class BookCreate(BaseModel):
    title: str = Field(min_length=1, max_length=250)
    description: str = Field(min_length=1)
    author_id: int
    category_id: int


class BookUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=250)
    description: str | None = Field(default=None, min_length=1)
    author_id: int | None = None
    category_id: int | None = None


class BookResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    author_id: int
    category_id: int
    author: AuthorBrief = Field(validation_alias="author_rel")
    category: CategoryBrief = Field(validation_alias="category_rel")