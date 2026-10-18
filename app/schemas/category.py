from pydantic import BaseModel, ConfigDict, Field


class category_create(BaseModel):
    name: str = Field(max_length=30)
    description: str = Field(max_length=5000)


class category_response(BaseModel):
    name: str = Field(max_length=30)
    description: str = Field(max_length=5000)


class category_update(BaseModel):
    name: str | None = Field(max_length=30)
    description: str | None = Field(max_length=5000)
