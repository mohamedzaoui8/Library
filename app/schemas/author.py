from pydantic import BaseModel, ConfigDict, Field


class AuthorCreate(BaseModel):
    firstname: str = Field(min_length=1, max_length=255)
    lastname: str = Field(min_length=1, max_length=255)
    biography: str


class AuthorUpdate(BaseModel):
    firstname: str | None = Field(default=None, min_length=1, max_length=255)
    lastname: str | None = Field(default=None, min_length=1, max_length=255)
    biography: str | None = None


class AuthorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    firstname: str
    lastname: str
    biography: str

class AuthorBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    firstname: str
    lastname: str