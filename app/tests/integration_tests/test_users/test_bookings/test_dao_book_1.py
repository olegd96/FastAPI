from datetime import datetime
from app.bookings.dao import BookingDAO
import uuid


async def test_and_get_booking():
    new_booking = await BookingDAO.add(
        user_id=uuid.UUID("3ede3539-f445-44fc-a81a-d036672603c8"),
        room_id=2,
        date_from=datetime.strptime("2023-07-10", "%Y-%m-%d"),
        date_to=datetime.strptime("2023-07-24", "%Y-%m-%d"),
    )

    assert new_booking.user_id == uuid.UUID("3ede3539-f445-44fc-a81a-d036672603c8")
    assert new_booking.room_id == 2

    new_booking = await BookingDAO.find_one_or_none(id=new_booking.id)

    assert new_booking is not None
