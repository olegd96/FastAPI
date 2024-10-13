from datetime import datetime
from typing import Literal
import uuid

from app.bookings.dao import BookingDAO

import pytest


@pytest.mark.parametrize(
    "user_id, room_id, date_from, date_to",
    [
        ("3ede3539-f445-44fc-a81a-d036672603c8", 2, "2030-06-15", "2030-06-20"),
        ("3ede3539-f445-44fc-a81a-d036672603c8", 3, "2030-06-15", "2030-06-20"),
        ("3ede3539-f445-44fc-a81a-d036672603b9", 4, "2030-06-15", "2030-06-20"),
        ("3ede3539-f445-44fc-a81a-d036672603b9", 4, "2030-06-15", "2030-06-20"),
    ],
)
async def test_bookings_crud(
    user_id: Literal["3ede3539-f445-44fc-a81a-d036672603c8"]
    | Literal["3ede3539-f445-44fc-a81a-d036672603b9"],
    room_id: Literal[2] | Literal[3] | Literal[4],
    date_from: Literal["2030-06-15"],
    date_to: Literal["2030-06-20"],
):
    new_booking = await BookingDAO.add(
        user_id=uuid.UUID(user_id),
        room_id=room_id,
        date_from=datetime.strptime(date_from, "%Y-%m-%d"),
        date_to=datetime.strptime(date_to, "%Y-%m-%d"),
    )

    assert new_booking["user_id"] == uuid.UUID(user_id)
    assert new_booking["room_id"] == room_id

    new_booking = await BookingDAO.find_one_or_none(id=new_booking.id)

    assert new_booking is not None

    await BookingDAO.delete(
        booking_id=new_booking.id,
        user_id=uuid.UUID(user_id),
    )

    deleted_booking = await BookingDAO.find_one_or_none(id=new_booking.id)
    assert deleted_booking is None
