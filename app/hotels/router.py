from datetime import date, datetime, timedelta
from fastapi_cache.decorator import cache
from typing import List, Optional
from fastapi import APIRouter, BackgroundTasks, Query
from app.hotels.dao import HotelsDAO
from app.hotels.models import Hotels
from app.hotels.schemas import SHotels, SHotelsInfo
from app.tasks.scheduled import send_cities_to_broker




from app.exceptions import DateFromCannotBeAfterDateTo, CannotBookHotelForLongPeriod



router = APIRouter(
    prefix="/hotels",
    tags=["Отели"],
)


@router.get("/search")
@cache(expire=150)
async def get_location(
    location: str,
) -> List:
    res = await HotelsDAO.find_location(location=location)
    return res

@router.get("/find_all")
async def find_all(background_task: BackgroundTasks):
    await send_cities_to_broker()


@router.get("/{location}")
@cache(expire=150)
async def get_hotels_by_location_and_time(location: str,
    date_from: date = Query(...,description=f"Например, {datetime.now().date()}"),
    date_to: date = Query(...,description=f"Например, {(datetime.now() + timedelta(days=14)).date()}"),
    ) -> List[SHotelsInfo]:
    if date_from > date_to:
        raise DateFromCannotBeAfterDateTo
    if (date_to - date_from).days > 31:
        raise CannotBookHotelForLongPeriod
    return await HotelsDAO.find_all(
        location=location, date_from=date_from, date_to=date_to)

@router.get("/id/{hotel_id}")
@cache(expire=150)
async def get_hotel_by_id(
    hotel_id: int) -> Optional[SHotels]:
    res = await HotelsDAO.find_one_or_none(id=hotel_id)
    return res




         
    