

from datetime import date
import uuid
from fastapi import Depends
from pydantic import TypeAdapter
from sqlalchemy import and_, func, insert, or_, select, delete, update
from app.bookings.models import Bookings
from app.dao.base import BaseDAO
from app.favourites.models import Favourites
from app.database import async_session_maker
from app.favourites.schemas import SFavList
from app.loger import logger

from app.hotels.models import Hotels
from app.hotels.rooms.models import Rooms
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import SQLAlchemyError
from app.users.models import Users


class FavDao(BaseDAO):

    models = Favourites

    @classmethod
    async def check_fav_hotel_room(
        cls,
        room_id: int,
        hotel_id: int,
        user_id: uuid.UUID | None = None,
        anonimous_id: str | None = None,
    ):
        if user_id:
            room_query = (select(Favourites)
                          .filter_by(user_id=user_id, room_id=room_id)
                          )

            stmt_like = (insert(Favourites)
                         .values(user_id=user_id,
                                 room_id=room_id,
                                 hotel_id=hotel_id)
                         .returning(Favourites.room_id,
                                    Favourites.user_id)
                         )

            stmt_dislike = (delete(Favourites)
                            .filter_by(user_id=user_id, room_id=room_id)
                            .returning(Favourites.room_id,
                                       Favourites.user_id)
                            )
        else:
            room_query = (select(Favourites)
                          .filter_by(anonimous_id=anonimous_id, room_id=room_id)
                          )

            stmt_like = (insert(Favourites)
                         .values(anonimous_id=anonimous_id,
                                 room_id=room_id,
                                 hotel_id=hotel_id)
                         .returning(Favourites.room_id,
                                    Favourites.anonimous_id)
                         )

            stmt_dislike = (delete(Favourites)
                            .filter_by(anonimous_id=anonimous_id, room_id=room_id)
                            .returning(Favourites.room_id,
                                       Favourites.anonimous_id)
                            )
        try:
            async with async_session_maker() as session:
                room = await session.execute(room_query)
                room_res = room.scalars().first()
                if not room_res:
                    res = await session.execute(stmt_like)
                    await session.commit()
                    return res.mappings().one()
                else:
                    res = await session.execute(stmt_dislike)
                    await session.commit()
                    return res.mappings().one()
        except (SQLAlchemyError, Exception) as e:
            if isinstance(e, SQLAlchemyError):
                msg = "Database Exc"
            elif isinstance(e, Exception):
                msg = "Unknown Exc"
            msg += ": Cannot like/unlike"
            extra = {
                "room_id": room_id,
                "anonimous_id": anonimous_id,
                "user_id": user_id,
            }
            logger.error(msg, extra=extra, exc_info=True)

    @classmethod
    async def get_all_fav(
        cls,
        limit = None,
        offset = None,
        **filter,
    ):
        # room_query = (
        #     select(Hotels.__table__.columns,
        #            Rooms.__table__.columns,
        #            Favourites.user_id, Favourites.room_id)
        #     .join(Rooms, Hotels.id == Rooms.hotel_id)
        #     .join(Favourites, Favourites.room_id == Rooms.id)
        #     .filter(Favourites.user_id == user_id)
        # )

        # cte = (
        #     select(
        #         room_query.c.name.label("hotel_name"),
        #         room_query.c.location,
        #         room_query.c.services.label("hotel_services"),
        #         room_query.c.rooms_quantity,
        #         room_query.c.image_id.label("hotel_image"),
        #         room_query.c.id_1.label("room_id"),
        #         room_query.c.name_1.label("room_name"),
        #         room_query.c.description.label("room_descr"),
        #         room_query.c.price,
        #         room_query.c.services_1.label("room_services"),
        #         room_query.c.quantity.label("room_quantity"),
        #         room_query.c.image_id_1.label("room_image")
        #     )
        # )

        room_query_1 = (select(Favourites)
                        .options(joinedload(Favourites.hotel))
                        .options(joinedload(Favourites.room))
                        .filter_by(**filter)
                        .limit(limit)
                        .offset(offset)
                        )

        async with async_session_maker() as session:
            rooms = await session.execute(room_query_1)
            rooms_res = rooms.scalars().all()
            rooms_res = [TypeAdapter(SFavList).validate_python(
                room).model_dump() for room in rooms_res]
            return rooms_res

    @classmethod
    async def count_all_fav(
        cls,
        **filter,
    ):
        room_query = (select(func.count(Favourites.user_id))
                        .filter_by(**filter)
                        ).group_by(Favourites.user_id)

        async with async_session_maker() as session:
            rooms = await session.execute(room_query)
            count_res = rooms.scalars().one()
            return count_res

    @classmethod
    async def get_fav_by_date(
        cls,
        date_from: date,
        date_to: date,
        **filter_by,
    ):
        booked = select(Rooms.__table__.columns,
                        (Rooms.quantity - func.count(Bookings.room_id)).label("rooms_left"),
                        ).select_from(Rooms).join(
            Bookings, Bookings.room_id == Rooms.id
        ).where(
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
        ).group_by(Bookings.room_id, Rooms.id).cte("booked")

        rooms_left = (select(Rooms.__table__.columns,
                             Rooms.quantity.label("rooms_left")).select_from(Rooms)
                      .where(
            Rooms.name.not_in(select(booked.c.name))
        )
            .union_all(select(booked)
                       .where(booked.c.rooms_left > 0))
        ).cte("rooms_left")

        room_query_1 = (select(Favourites)
                        .options(joinedload(Favourites.hotel))
                        .options(joinedload(Favourites.room))
                        .filter_by(**filter_by)
                        .where(Favourites.room_id.in_(select(rooms_left.c.id)))
                        )

        async with async_session_maker() as session:
            rooms = await session.execute(room_query_1)
            rooms_res = rooms.scalars().all()
            rooms_res = [TypeAdapter(SFavList).validate_python(
                room).model_dump() for room in rooms_res]
            return rooms_res

    @classmethod
    async def from_anon_to_reg(cls, anonimous_id: str, user: Users):
        query = (update(Favourites)
                 .where(
            and_(
                Favourites.anonimous_id == anonimous_id,
                Favourites.room_id.not_in(
                    select(Favourites.room_id).filter_by(user_id=user.id))
            )
        )
            .values(user_id=user.id, anonimous_id="")
            .returning(Favourites.user_id)
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
            msg += ": Cannot replace anon_fav to user_fav"
            extra = {
                "anonimous_id": anonimous_id,
                "user_id": user.id,
            }
            logger.error(msg, extra=extra, exc_info=True)
