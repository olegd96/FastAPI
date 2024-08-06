from pydantic import BaseModel, ConfigDict
from typing import Any, List
from sqlalchemy.dialects.postgresql import TSVECTOR

class SHotels(BaseModel):
    id: int
    name: str
    city: str
    location: str
    services: List[str]
    rooms_quantity: int
    image_id: int
    rate: float
    tsv: Any

    model_config = ConfigDict(from_attributes=True)


class SHotelsInfo(SHotels):
    rooms_left: int

    model_config = ConfigDict(from_attributes=True)