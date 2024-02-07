
from pydantic import BaseModel, ConfigDict

class SFavNew(BaseModel):
    id: int

    model_config = ConfigDict(from_attributes=True) 


class SFav(BaseModel):
    id: int
    user_id: int|None
    anonimous_id: int|None
    hotel_id: int|None
    room_id: int|None