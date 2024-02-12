from datetime import date



from app.loger import logger
from app.cart.models import Carts
from app.bookings.models import Bookings
from app.hotels.rooms.models import Rooms
from app.hotels.models import Hotels
from app.database import async_session_maker
from app.dao.base import BaseDAO
from app.exceptions import UserIsNotPresentException
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, and_, delete, func, insert, select, update, values
from sqlalchemy.exc import SQLAlchemyError

from app.users.models import Users



class CartDao(BaseDAO):
    models = Carts

    @classmethod
    async def add(
        cls,
        room_id: int,
        date_from: date,
        date_to: date,
        anonimous_id: str = "",
        user_id: int|None = None,
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
        WH
        
        ERE rooms.id = 1
        GROUP BY rooms.quantity, booked_rooms.room_id
        """
        try:
            booked_rooms = (
                select(Bookings)
                .where(
                    and_(
                        Bookings.room_id == room_id,
                        and_(
                            Bookings.date_to >= date_to, Bookings.date_from <= date_from
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
                    add_booking_to_cart = (
                        insert(Carts)
                        .values(
                            room_id=room_id,
                            user_id=user_id,
                            date_from=date_from,
                            date_to=date_to,
                            price=price,
                            anonimous_id=anonimous_id,
                        )
                        .returning(
                            Carts.id,
                            Carts.room_id,
                            Carts.user_id,
                            Carts.anonimous_id,
                            Carts.date_from,
                            Carts.date_to,
                        )
                    )

                    new_cart_rec = await session.execute(add_booking_to_cart)
                    await session.commit()
                    return new_cart_rec.mappings().one()
                else:
                    return None

        except (SQLAlchemyError, Exception) as e:
            if isinstance(e, SQLAlchemyError):
                msg = "Database Exc"
            elif isinstance(e, Exception):
                msg = "Unknown exc"
            msg += ": Cannot add booking to cart"
            extra = {
                "user_id": user_id,
                "room_id": room_id,
                "date_from": date_from,
                "date_to": date_to,
                "anonimous_id": anonimous_id,
            }
            logger.error(msg, extra=extra, exc_info=True)

    @classmethod
    async def delete(cls, booking_id: int, user_id: int|None = None, anonimous_id: str = "",):
        try:
            b_user_id = select(Carts.user_id).where(Carts.id == booking_id)
            async with async_session_maker() as session:
                b_user_id = await session.execute(b_user_id)
                b_user_id = b_user_id.scalar()
                if b_user_id != user_id:
                    raise UserIsNotPresentException
                delete_booking = (update(Carts)
                                .values(deleted=True)
                                .where(Carts.id == booking_id)
                                .returning(Carts.id)
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
            msg += ": Cannot delete booking from cart"
            extra = {
                "current_user_id": user_id,
                "owner_booking_id": b_user_id,
            }
            logger.error(msg, extra=extra, exc_info=True)

    @classmethod
    async def find_all_with_images(cls, user_id: int|None = None, anonimous_id: str = "",):
        if user_id:
            query = (
                select(
                    Carts.__table__.columns,
                    Rooms.__table__.columns,
                    Hotels.__table__.columns,
                )
                .join(Rooms, Rooms.id == Carts.room_id, isouter=True)
                .join(Hotels, Hotels.id == Rooms.hotel_id)
                .where(
                    and_(Carts.user_id == user_id, 
                         Carts.deleted == False))
            )
        else:
            query = (
                select(
                    Carts.__table__.columns,
                    Rooms.__table__.columns,
                    Hotels.__table__.columns,
                )
                .join(Rooms, Rooms.id == Carts.room_id, isouter=True)
                .join(Hotels, Hotels.id == Rooms.hotel_id)
                .where(
                    and_(Carts.anonimous_id == anonimous_id,
                         Carts.deleted == False))
            )
        async with async_session_maker() as session:
            result = await session.execute(query)
            return result.mappings().all()
    
    @classmethod
    async def from_anon_to_reg(cls, anonimous_id: str, user: Users):
        query = (update(Carts)
                .where(Carts.anonimous_id == anonimous_id)
                .values(user_id=user.id, anonimous_id="")
                .returning(Carts.user_id)
        )
        try:
            async with async_session_maker() as session:
                result = await session.execute(query)
                await session.commit()
            return result.scalar()
        except (SQLAlchemyError, Exception) as e:
            if isinstance(e, SQLAlchemyError):
                msg = "Database Exc"
            elif isinstance(e, Exception):
                msg = "Unknown Exc"
            msg += ": Cannot replace anon_cart to user_cart"
            extra = {
                "user_id": user.id,
                "anon_id": anonimous_id,
            }
            logger.error(msg, extra=extra, exc_info=True)
    
    