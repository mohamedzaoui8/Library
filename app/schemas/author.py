from typing import Optional

from pydantic import BaseModel


class create_author(BaseModel):
    first_name: str
    last_name: str
    bio: str

class author_update(BaseModel):
    first_name : str | None=None
    last_name_name : str | None=None
    bio : str | None=None

