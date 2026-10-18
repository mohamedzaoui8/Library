from pydantic import BaseModel, ConfigDict, Field

# title ,author ,description ,


class book_create(BaseModel):
    title: str = Field(max_length=50)
    author: str = Field(max_length=50)
    description: str = Field(default=None, max_length=5000)


class book_response(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    author: str
    description: str


class book_update(BaseModel):
    title: str | None = Field(max_length=50)
    author: str | None = Field(max_length=50)
    description: str | None = Field(default=None, max_length=5000)
