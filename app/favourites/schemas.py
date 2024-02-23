
from typing import Any, List, Optional
import uuid
from pydantic import BaseModel, ConfigDict
from sqlalchemy import JSON
from app.favourites.models import Favourites



from app.hotels.rooms.schemas import SRoom
from app.hotels.schemas import SHotels
from app.hotels.rooms.schemas import SRoom


class SFavNew(BaseModel):
    id: int
    h_id: int

    model_config = ConfigDict(from_attributes=True)


class SFav(BaseModel):
    id: int
    user_id: uuid.UUID | None
    anonimous_id: str | None
    hotel_id: int | None
    room_id: int | None
    

    model_config = ConfigDict(from_attributes=True)
    

class SFavList(SFav):
    hotel: "SHotels"
    room: "SRoom"

