import uuid
from datetime import date, timedelta

from pydantic import TypeAdapter
from sqlalchemy import Null, and_, delete, desc, func, insert, or_, select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload

from app.bookings.models import Bookings
from app.bookings.schemas import (
    SBooking,
    SBookingInfo,
    SBookingWithRoom,
    SBookingWithRoomAndUser,
)
from app.dao.base import BaseDAO
from app.database import async_session_maker, async_session_taskmaker
from app.exceptions import UserIsNotPresentException
from app.hotels.dao import HotelsDAO
from app.hotels.models import Hotels
from app.hotels.rooms.models import Rooms
from app.hotels.rooms.schemas import SRoomWithHotel
from app.loger import logger
from app.users.models import Users


class BookingDAO(BaseDAO):
    models = Bookings

    @classmethod
    async def add(
        cls,
        user_id: uuid.UUID,
        room_id: int,
        date_from: date,
        date_to: date,
    ):
        """
        WITH booked_rooms AS (
        SELECT *FROM Bookings
        WHERE room_id = 1 AND
        (date_to >= '2023-06-20' AND
        date_from <= '2023-06-15')
        )
        SELECT rooms.quantity - COUNT(booked_rooms.room_id) FROM rooms
        LEFT JOIN booked_rooms ON booked_rooms.room_id = rooms.id
        WHERE rooms.id = 1
        GROUP BY rooms.quantity, booked_rooms.room_id
        """
        try:
            booked_rooms = (
                select(Bookings)
                .where(
                    and_(
                        Bookings.room_id == room_id,
                        or_(
                            and_(
                                Bookings.date_from >= date_from,
                                Bookings.date_from <= date_to,
                            ),
                            and_(
                                Bookings.date_from <= date_from,
                                Bookings.date_to > date_from,
                            ),
                        ),
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

        except (SQLAlchemyError, Exception) as e:
            if isinstance(e, SQLAlchemyError):
                msg = "Database Exc"
            elif isinstance(e, Exception):
                msg = "Unknown exc"
            msg += ": Cannot add booking"
            extra = {
                "user_id": user_id,
                "room_id": room_id,
                "date_from": date_from,
                "date_to": date_to,
            }
            logger.error(msg, extra=extra, exc_info=True)

    @classmethod
    async def delete(cls, booking_id: int, user_id: uuid.UUID):
        try:
            b_user_id = select(Bookings.user_id).where(Bookings.id == booking_id)
            async with async_session_maker() as session:
                b_user_id = await session.execute(b_user_id)
                b_user_id = b_user_id.scalar()
                if b_user_id != user_id:
                    raise UserIsNotPresentException
                delete_booking = (
                    delete(Bookings)
                    .where(Bookings.id == booking_id)
                    .returning(Bookings.id)
                )
                res = await session.execute(delete_booking)
                await session.commit()
                return res.mappings().one()
        except (SQLAlchemyError, UserIsNotPresentException, Exception) as e:
            if isinstance(e, SQLAlchemyError):
                msg = "Database Exc"
            elif isinstance(e, UserIsNotPresentException):
                msg = "User Exc"
            elif isinstance(e, Exception):
                msg = "Unknown Exc"
            msg += ": Cannot delete booking"
            extra = {
                "current_user_id": user_id,
                "owner_booking_id": b_user_id,
            }
            logger.error(msg, extra=extra, exc_info=True)

    @classmethod
    async def find_all_with_images(cls, user_id: uuid.UUID):
        query = (
            select(
                Bookings.__table__.columns,
                Rooms.__table__.columns,
                Hotels.__table__.columns,
            )
            .join(Rooms, Rooms.id == Bookings.room_id, isouter=True)
            .join(Hotels, Hotels.id == Rooms.hotel_id)
            .where(
                and_(
                    Bookings.user_id == user_id,
                    Bookings.deleted == False,
                    Bookings.date_to > date.today(),
                )
            )
        )
        async with async_session_maker() as session:
            result = await session.execute(query)
            return result.mappings().all()

    @classmethod
    async def find_all_nearest_bookings(cls, day_delta: int):
        async with async_session_taskmaker() as session:
            book_query = (
                select(Bookings)
                .options(joinedload(Bookings.user))
                .options(joinedload(Bookings.room))
                .filter(
                    and_(
                        date.today() <= Bookings.date_from - timedelta(days=day_delta),
                        Bookings.deleted == False,
                    )
                )
            )

            bookings = await session.execute(book_query)
            bookings = bookings.scalars().all()
            bookings = [
                TypeAdapter(SBookingWithRoomAndUser).validate_python(book).model_dump()
                for book in bookings
            ]
            return bookings

    @classmethod
    async def find_all_past_bookings(cls, user: Users, limit=None, offset=None):
        async with async_session_maker() as session:
            query = (
                select(Bookings)
                .options(joinedload(Bookings.room))
                .filter(
                    and_(
                        Bookings.date_to <= date.today(),
                        Bookings.deleted == False,
                        Bookings.user_id == user.id,
                    )
                )
                .limit(limit)
                .offset(offset)
            )

            past_bookings = await session.execute(query)
            past_bookings = past_bookings.scalars().all()
            past_bookings = [
                TypeAdapter(SBookingWithRoom).validate_python(book).model_dump()
                for book in past_bookings
            ]
            return past_bookings

    @classmethod
    async def count_all_past(cls, user: Users):
        async with async_session_maker() as session:
            query = (
                select(func.count(Bookings.user_id))
                .filter(
                    and_(
                        Bookings.date_to <= date.today(),
                        Bookings.deleted == False,
                        Bookings.user_id == user.id,
                    )
                )
                .group_by(Bookings.user_id)
            )

            past_bookings = await session.execute(query)
            past_bookings = past_bookings.scalars().one_or_none()
            if past_bookings:
                return past_bookings
            return 0

    @classmethod
    async def find_all_past_bookings_by_date(
        cls,
        user: Users,
        date_from: date,
        date_to: date,
    ):
        booked = (
            select(
                Rooms.__table__.columns,
                (Rooms.quantity - func.count(Bookings.room_id)).label("rooms_left"),
            )
            .select_from(Rooms)
            .join(Bookings, Bookings.room_id == Rooms.id)
            .where(
                or_(
                    and_(
                        Bookings.date_from >= date_from,
                        Bookings.date_from <= date_to,
                    ),
                    and_(
                        Bookings.date_from <= date_from,
                        Bookings.date_to > date_from,
                    ),
                ),
            )
            .group_by(Bookings.room_id, Rooms.id)
            .cte("booked")
        )

        rooms_left = (
            select(Rooms.__table__.columns, Rooms.quantity.label("rooms_left"))
            .select_from(Rooms)
            .where(Rooms.name.not_in(select(booked.c.name)))
        ).union_all(select(booked).where(booked.c.rooms_left > 0))

        room_query = (
            select(Bookings)
            .options(joinedload(Bookings.room))
            .filter(
                and_(
                    Bookings.date_to <= date.today(),
                    Bookings.deleted == False,
                    Bookings.user_id == user.id,
                )
            )
            .where(Bookings.room_id.in_(select(rooms_left.c.id)))
        )

        async with async_session_maker() as session:
            past_bookings_by_date = await session.execute(room_query)
            past_bookings_by_date = past_bookings_by_date.scalars().all()
            past_bookings_by_date = [
                TypeAdapter(SBookingWithRoom).validate_python(book).model_dump()
                for book in past_bookings_by_date
            ]
            return past_bookings_by_date

    @classmethod
    async def get_most_popular_location(
        cls,
    ):
        bookings = (
            select(Bookings.room_id, func.count(Bookings.room_id).label("book_count"))
            .order_by(desc("book_count"))
            .group_by(Bookings.room_id)
            .limit(6)
        ).cte("bookings")

        hotels = (
            select(Rooms)
            .options(joinedload(Rooms.hotel))
            .filter(Rooms.id.in_(select(bookings.c.room_id)))
        )

        async with async_session_maker() as session:
            res = await session.execute(hotels)
            res = res.scalars().all()
            rooms_hotels = [
                TypeAdapter(SRoomWithHotel).validate_python(r).model_dump() for r in res
            ]
            return rooms_hotels

    @classmethod
    async def set_avg_by_room_id(
        cls,
        room_id: int,
    ):
        try:
            rooms_avg = (
                select(
                    Bookings.room_id,
                    Rooms.hotel_id.label("hotel_id"),
                    func.round((func.avg(Bookings.rate)), 3).label("avg_rate"),
                )
                .where(and_(Bookings.rate != 0, Bookings.room_id == room_id))
                .join(Rooms, Rooms.id == Bookings.room_id)
                .group_by(Bookings.room_id, Rooms.hotel_id)
            ).cte("rooms_avg")

            hotels_avg = (
                select(
                    rooms_avg.c.hotel_id,
                    func.round(func.avg(rooms_avg.c.avg_rate), 3).label("hotel_avg"),
                ).group_by(rooms_avg.c.hotel_id)
            ).cte("hotels_avg")

            hotel_rate = (
                update(Hotels)
                .where(Hotels.id == hotels_avg.c.hotel_id)
                .values(rate=hotels_avg.c.hotel_avg)
                .returning(Hotels.id, Hotels.rate)
            )

            async with async_session_maker() as session:
                res = await session.execute(hotel_rate)
                await session.commit()
                return res.mappings().one_or_none()
        except (SQLAlchemyError, UserIsNotPresentException, Exception) as e:
            if isinstance(e, SQLAlchemyError):
                msg = "Database Exc"
            elif isinstance(e, UserIsNotPresentException):
                msg = "User Exc"
            elif isinstance(e, Exception):
                msg = "Unknown Exc"
            msg += ": Cannot update hotel_rate"
            extra = {
                "room_id": room_id,
            }
            logger.error(msg, extra=extra, exc_info=True)
