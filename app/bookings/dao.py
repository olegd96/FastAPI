from datetime import date

from sqlalchemy import insert, select, delete, and_, func
from app.bookings.models import Bookings
from app.dao.base import BaseDAO
from app.exceptions import UserIsNotPresentException
from app.hotels.models import Hotels
from app.hotels.rooms.models import Rooms
from app.database import async_session_maker


class BookingDAO(BaseDAO):
    models = Bookings

    @classmethod
    async def add(
        cls,
        user_id: int,
        room_id: int,
        date_from: date,
        date_to: date,
    ):
        """
        WITH booked_rooms AS (
        SELECT *FROM bookings
        WHERE room_id = 1 AND
        (date_to >= '2023-06-20' AND
        date_from <= '2023-06-15')
        )
        SELECT rooms.quantity - COUNT(booked_rooms.room_id) FROM rooms
        LEFT JOIN booked_rooms ON booked_rooms.room_id = rooms.id
        WHERE rooms.id = 1
        GROUP BY rooms.quantity, booked_rooms.room_id
        """

        booked_rooms = (
            select(Bookings)
            .where(
                and_(
                    Bookings.room_id == room_id,
                    and_(Bookings.date_to >= date_to, Bookings.date_from <= date_from),
                )
            )
            .cte("booked_rooms")
        )

        get_rooms_left = (
            select(
                (Rooms.quantity - func.count(booked_rooms.c.room_id)).label(
                    "rooms_left"
                )
            )
            .select_from(Rooms)
            .join(booked_rooms, booked_rooms.c.room_id == Rooms.id, isouter=True)
            .where(Rooms.id == room_id)
            .group_by(Rooms.quantity, booked_rooms.c.room_id)
        )
        # print(get_rooms_left.compile(engine, compile_kwargs={"literal_binds": True}))
        async with async_session_maker() as session:
            rooms_left = await session.execute(get_rooms_left)
            rooms_left: int = rooms_left.scalar()
            if rooms_left > 0:
                get_price = select(Rooms.price).filter_by(id=room_id)
                price = await session.execute(get_price)
                price: int = price.scalar()
                add_booking = (
                    insert(Bookings)
                    .values(
                        room_id=room_id,
                        user_id=user_id,
                        date_from=date_from,
                        date_to=date_to,
                        price=price,
                    )
                    .returning(
                        Bookings.id,
                        Bookings.user_id,
                        Bookings.room_id,
                        Bookings.date_from,
                        Bookings.date_to,
                    )
                )

                new_booking = await session.execute(add_booking)
                await session.commit()
                return new_booking.mappings().one()
            else:
                return None

    @classmethod
    async def delete(cls, booking_id: int, user_id: int):
        b_user_id = select(Bookings.user_id).where(Bookings.id == booking_id)
        async with async_session_maker() as session:
            b_user_id = await session.execute(b_user_id)
            b_user_id = b_user_id.scalar()
            if b_user_id != user_id:
                raise UserIsNotPresentException
            delete_booking = delete(Bookings).where(Bookings.id == booking_id)
            await session.execute(delete_booking)
            await session.commit()

    @classmethod
    async def find_all_with_images(cls, user_id: int):
        query = (
            select(
                Bookings.__table__.columns,
                Rooms.__table__.columns,
                Hotels.__table__.columns,
            )
            .join(Rooms, Rooms.id == Bookings.room_id, isouter=True)
            .join(Hotels, Hotels.id == Rooms.hotel_id)
            .where(Bookings.user_id == user_id)
        )
        async with async_session_maker() as session:
            result = await session.execute(query)
            return result.mappings().all()
