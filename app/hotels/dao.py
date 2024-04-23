from datetime import date
from sqlalchemy import all_, desc, or_, select, func, and_
from app.bookings.models import Bookings
from app.dao.base import BaseDAO
from app.database import async_session_maker
from app.exceptions import DateFromCannotBeAfterDateTo
from app.hotels.models import Hotels
from app.hotels.rooms.models import Rooms

class HotelsDAO(BaseDAO):

    models = Hotels

    @classmethod
    async def find_all(cls, location:str, date_from: date, date_to:date, limit=None, offset=None):
        """
        WITH booked_rooms AS (
        select room_id, COUNT(room_id) as rooms_booked
        from bookings
        where date_from <= date_from and date_to >= date_to
        group by room_id),
        booked_hotels AS(
        select hotel_id, SUM(rooms.quantity - COALESCE(rooms_booked, 0)) AS rooms_left
        FROM rooms
        LEFT JOIN booked_rooms ON booked_rooms.room_id = rooms.id
        GROUP BY hotel_id)

        SELECT * FROM HOTELS
        LEFT JOIN booked_hotels ON booked_hotels.hotel_id = hotel_id
        WHERE rooms_left > 0 AND LOCATION LIKE '%Алтай%'
        """

        if date_from > date_to:
            raise DateFromCannotBeAfterDateTo


        booked_rooms = (select(Bookings.room_id, func.count(Bookings.room_id).label("rooms_booked"))
        .select_from(Bookings)
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
        .group_by(Bookings.room_id)

        
        .cte("booked_rooms")
        )

        booked_hotels = (
            select(Rooms.hotel_id, func.sum(
            Rooms.quantity - func.coalesce(booked_rooms.c.rooms_booked, 0)).label("rooms_left"))
            .select_from(Rooms)
            .join(booked_rooms, booked_rooms.c.room_id == Rooms.id, isouter=True)
            .group_by(Rooms.hotel_id)
            .cte("booked_hotels")
            )
        
        get_hotels_with_rooms = (select(Hotels.__table__.columns,
                                       booked_hotels.c.rooms_left,
                                       ).join(booked_hotels, booked_hotels.c.hotel_id == Hotels.id , isouter=True)
                                        .where(
                                            and_(booked_hotels.c.rooms_left>0,
                                                Hotels.location.like(f"%{location}%")
                                                )
                                                
                                        )
                                        .limit(limit)
                                        .offset(offset)
                                        )
        
        async with async_session_maker() as session:
            hotels_with_rooms = await session.execute(get_hotels_with_rooms)
            return hotels_with_rooms.mappings().all()


    @classmethod
    async def hotels_count(cls, location:str, date_from: date, date_to:date):
        if date_from > date_to:
            raise DateFromCannotBeAfterDateTo


        booked_rooms = (select(Bookings.room_id, func.count(Bookings.room_id).label("rooms_booked"))
        .select_from(Bookings)
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
        .group_by(Bookings.room_id)

        
        .cte("booked_rooms")
        )

        booked_hotels = (
            select(Rooms.hotel_id, func.sum(
            Rooms.quantity - func.coalesce(booked_rooms.c.rooms_booked, 0)).label("rooms_left"))
            .select_from(Rooms)
            .join(booked_rooms, booked_rooms.c.room_id == Rooms.id, isouter=True)
            .group_by(Rooms.hotel_id)
            .cte("booked_hotels")
            )
        
        get_hotels_with_rooms = (select(Hotels.__table__.columns,
                                       booked_hotels.c.rooms_left,
                                       ).join(booked_hotels, booked_hotels.c.hotel_id == Hotels.id , isouter=True)
                                        .where(
                                            and_(booked_hotels.c.rooms_left>0,
                                                Hotels.location.like(f"%{location}%")
                                                )     
                                        )
                                        )
        
        get_hotels_count = select(func.count()).select_from(get_hotels_with_rooms)
        
        async with async_session_maker() as session:
            hotels_count = await session.execute(get_hotels_count)
            return hotels_count.scalars().one()


    @classmethod
    async def find_location(
        cls,
        location: str,
    ):
        location_query = (
            select(Hotels.location)
            .order_by(desc(Hotels.location))
            .filter(
                Hotels.location.ilike(f"%{location}%")
            )
    
        )

        async with async_session_maker() as session:
            locations = await session.execute(location_query)
            locations = locations.unique().scalars().all()
            return locations

    