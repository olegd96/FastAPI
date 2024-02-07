from datetime import date, datetime
from pydantic import BaseModel, ConfigDict

class SCart(BaseModel):
    id: int
    room_id: int
    user_id: int|None
    anonimous_id: str|None
    date_from: date
    date_to: date
    price: int
    total_cost: int
    total_days: int
    deleted: bool
    created: datetime

    model_config = ConfigDict(from_attributes=True)


class SCartInfo(BaseModel):
    id: int
    room_id: int
    user_id: int|None
    anonimous_id: str|None
    date_from: date
    date_to: date