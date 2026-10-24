import re

from pydantic import BaseModel, EmailStr, Field, field_validator


class user_create(BaseModel):
    email: EmailStr
    username: str = Field(max_length=50)
    password: str = Field(min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if not re.search(r"[A-Z]", value):
            raise ValueError("Password must contain an uppercase letter")

        if not re.search(r"[a-z]", value):
            raise ValueError("Password must contain a lowercase letter")

        if not re.search(r"\d", value):
            raise ValueError("Password must contain a digit")

        if not re.search(r"[^A-Za-z0-9]", value):
            raise ValueError("Password must contain a special character")

        return value


class user_response(BaseModel):
    id: int
    email: EmailStr
    username: str

class user_login(BaseModel):
    email: EmailStr
    password: str
