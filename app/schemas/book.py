from pydantic import BaseModel, ConfigDict, Field

# title ,author ,description ,


class book_create(BaseModel):
    title: str = Field(max_length=250)
    description: str
    author_id: int
    category_id: int

class book_response(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    author_id: int
    category_id: int

class book_update(BaseModel):
    title: str | None = Field(default=None, max_length=250)
    description: str | None = Field(default=None, max_length=5000)
    author_id: int | None = None
    category_id: int | None = None