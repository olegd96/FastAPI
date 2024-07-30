import asyncio
from datetime import date, datetime, timedelta
from typing import List

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi_versioning import version
from pydantic import TypeAdapter
from sqlalchemy import select

from app.bookings.dao import BookingDAO
from app.bookings.models import Bookings
from app.bookings.schemas import (
    SBooking,
    SBookingInfo,
    SBookingRate,
    SBookingWithRoom,
    SBookingWithRoomAndUser,
    SNewBooking,
)
from app.exceptions import BookingMiss, RoomCannotBeBooked
from app.hotels.rooms.schemas import SRoomWithHotel
from app.tasks.scheduled import notice
from app.tasks.tasks import send_booking_confirmation_email
from app.users.dependencies import get_current_user
from app.users.models import Users

router = APIRouter(
    prefix="/bookings",
    tags=["Бронирования"],
)


@router.get("")
#@version(1)
async def get_bookings(user: Users = Depends(get_current_user)) -> list[SBookingInfo]:
    return await BookingDAO.find_all_with_images(user_id=user.id)

@router.post("")
#@version(1)
async def add_booking(
    booking: SNewBooking,
    user: Users = Depends(get_current_user)
) -> SNewBooking:
    booking = await BookingDAO.add(
        user.id,
        booking.room_id,
        booking.date_from,
        booking.date_to)
    if not booking:
        raise RoomCannotBeBooked
    booking = TypeAdapter(SNewBooking).validate_python(booking).model_dump()
    send_booking_confirmation_email.delay(booking=booking, email_to=user.email)
    return booking


@router.delete("/{booking_id}")
#@version(1)
async def delete_booking(
    booking_id: int,
    user: Users = Depends(get_current_user),
):
    res = await BookingDAO.delete(booking_id=booking_id, user_id=user.id)
    if not res:
        raise BookingMiss
    return res


@router.get('/notice', status_code=201)
async def get_notice_list(
    delta:int
) -> List[SBookingWithRoomAndUser]:
    res = await BookingDAO.find_all_nearest_bookings(delta)
    return res

@router.get("/past")
async def get_past_bookings(
    limit=3,
    offset=0,
    user: Users = Depends(get_current_user),
) -> List[SBookingWithRoom]:
    past_book_query = await BookingDAO.find_all_past_bookings(user)
    return past_book_query

@router.get("/past_by_date")
async def get_past_bookings_by_date(
    date_from: date = Query(...,
                            description=f"Например, {datetime.now().date()}"),
    date_to: date = Query(
        ..., description=f"Например, {(datetime.now() + timedelta(days=14)).date()}"),
    user: Users = Depends(get_current_user),
) -> List[SBookingWithRoom]:
    past_book_query = await BookingDAO.find_all_past_bookings_by_date(user, date_from, date_to)
    return past_book_query


@router.get("/popular")
async def get_most_popular() -> list[SRoomWithHotel]:
    popular = await BookingDAO.get_most_popular_location()
    return popular

@router.post("/rate")
async def check_rate(
    data: SBookingRate,
    user: Users = Depends(get_current_user),
) -> SBooking:
    data = data.model_dump()
    rate = await BookingDAO.update(Bookings.id==int(data['ids']),  data={"rate": int(data['rate'])})
    return rate