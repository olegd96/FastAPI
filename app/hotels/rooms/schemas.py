from typing import Optional
from pydantic import BaseModel, ConfigDict

class SRoom(BaseModel):
    id: int
    hotel_id: int
    name: str
    description: Optional[str]
    price: int
    services: list[str]
    quantity: Optional[int]
    image_id: Optional[int]

    model_config = ConfigDict(from_attributes=True)

class SRoomInfo(SRoom):
    total_cost: int
    rooms_left: int  

    model_config = ConfigDict(from_attributes=True)