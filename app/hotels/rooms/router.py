from datetime import date, datetime, timedelta

from typing import List
from fastapi_cache.decorator import cache
from fastapi import Query
from app.exceptions import CannotBookHotelForLongPeriod, DateFromCannotBeAfterDateTo


from app.hotels.rooms.dao import RoomsDAO

from app.hotels.rooms.schemas import SRoomInfo
from app.hotels.router import router


@router.get("/{hotel_id}/rooms")
@cache(expire=150)
async def get_rooms_by_time(
    hotel_id: int,
    date_from: date = Query(...,
                            description=f"Например, {datetime.now().date()}"),
    date_to: date = Query(
        ..., description=f"Например, {(datetime.now() + timedelta(days=14)).date()}"),
) -> List[SRoomInfo]:
    if date_from > date_to:
        raise DateFromCannotBeAfterDateTo
    if (date_to - date_from).days > 31:
        raise CannotBookHotelForLongPeriod
    return await RoomsDAO.find_all(hotel_id, date_from, date_to)
