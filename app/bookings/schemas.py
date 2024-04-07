from datetime import date
from typing import Optional
import uuid
from pydantic import BaseModel, ConfigDict, EmailStr

from app.hotels.rooms.schemas import SRoom

class SBooking(BaseModel):
    id : int 
    room_id : int
    user_id : uuid.UUID
    date_from : date
    date_to : date
    price : int
    total_cost : int
    total_days : int
    rate: Optional[int]
    
    model_config = ConfigDict(from_attributes=True)


class SBookingInfo(SBooking):
    image_id: int
    name: str
    description: Optional[str]
    services: list[str]   
    name_1: str
    location: str
   
    model_config = ConfigDict(from_attributes=True)


class SNewBooking(BaseModel):
    room_id: int
    date_from: date
    date_to: date


class SBookingWithRoom(SBooking):
    room: "SRoom"

    model_config = ConfigDict(from_attributes=True)

class SBookingRate(BaseModel):
    rate: str
    ids: str