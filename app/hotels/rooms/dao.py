from datetime import date

from sqlalchemy import and_, func, or_, select
from app.bookings.models import Bookings
from app.dao.base import BaseDAO
from app.exceptions import DateFromCannotBeAfterDateTo
from app.hotels.rooms.models import Rooms
from app.database import async_session_maker


class RoomsDAO(BaseDAO):
    models = Rooms

    @classmethod
    async def find_all(cls, hotel_id: int, date_from: date, date_to: date):
        """
        with booked as(
        SELECT room_id, rooms.name, COUNT(room_id) as booked_count, quantity - COUNT(room_id) as rooms_left FROM bookings
        JOIN rooms ON room_id = rooms.id
        WHERE hotel_id = 1 AND date_from <= '2023-06-15' AND date_to >= '2023-06-25'
        GROUP BY room_id, rooms.name, rooms.quantity)

        SELECT * from booked
        UNION
        SELECT rooms.id, rooms.name, 0, quantity FROM rooms 
        WHERE hotel_id = 1 and name not in (SELECT name from booked)

        """
        if date_from > date_to:
            raise DateFromCannotBeAfterDateTo
        
        booked = select(Rooms.__table__.columns,
                        (Rooms.price * (date_to - date_from).days).label("total_cost"),
                        (Rooms.quantity - func.count(Bookings.room_id)).label("rooms_left"),
                        ).select_from(Rooms).join(
                         Bookings, Bookings.room_id == Rooms.id   
                        ).where(
                            and_(Rooms.hotel_id == hotel_id,
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
                                ),
                            ).group_by(Bookings.room_id, Rooms.id).cte("booked")

        
        rooms_left =(select(Rooms.__table__.columns, 
                (Rooms.price * (date_to - date_from).days).label("total_cost"),
                Rooms.quantity.label("rooms_left")).select_from(Rooms).where(
                    and_(
                    Rooms.hotel_id == hotel_id,
                    Rooms.name.not_in(select(booked.c.name)),
                    
                )
        )).union_all(select(booked).where(booked.c.rooms_left > 0))


        async with async_session_maker() as session:
            rooms = await session.execute(rooms_left)
            return rooms.mappings().all()