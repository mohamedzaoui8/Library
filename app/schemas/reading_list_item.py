from pydantic import BaseModel, ConfigDict, Field


class reading_list_item_create(BaseModel):
    book_id: int



class reading_list_item_response(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    book_id: int


