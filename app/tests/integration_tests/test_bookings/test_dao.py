from datetime import datetime
from operator import ne

from app.bookings.dao import BookingDAO

import pytest

@pytest.mark.parametrize("user_id, room_id, date_from, date_to", [
    (2, 2, "2030-06-15", "2030-06-20"),
    (2, 3, "2030-06-15", "2030-06-20"),
    (1, 4, "2030-06-15", "2030-06-20"),
    (1, 4, "2030-06-15", "2030-06-20"),

])
async def test_bookings_crud(user_id, room_id, date_from , date_to):
    new_booking = await BookingDAO.add(
        user_id=user_id, 
        room_id=room_id, 
        date_from=datetime.strptime(date_from, "%Y-%m-%d"), 
        date_to=datetime.strptime(date_to, "%Y-%m-%d"),
        )
    
    assert new_booking["user_id"] == user_id
    assert new_booking["room_id"] == room_id

    new_booking = await BookingDAO.find_one_or_none(id=new_booking.id)

    assert new_booking is not None

    await BookingDAO.delete(
        booking_id=new_booking.id,
        user_id=user_id,
    )

    deleted_booking = await BookingDAO.find_one_or_none(id=new_booking.id)
    assert deleted_booking is None