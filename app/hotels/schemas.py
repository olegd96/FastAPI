from pydantic import BaseModel, ConfigDict
from typing import List

class SHotels(BaseModel):
    id: int
    name: str
    city: str
    location: str
    services: List[str]
    rooms_quantity: int
    image_id: int
    rate:float

    model_config = ConfigDict(from_attributes=True)


class SHotelsInfo(SHotels):
    rooms_left: int

    model_config = ConfigDict(from_attributes=True)