

from fastapi import Depends
from sqlalchemy import insert, select, delete
from app.dao.base import BaseDAO
from app.favourites.models import Favourites
from app.database import async_session_maker


class FavDao(BaseDAO):

    models = Favourites

    @classmethod
    async def check_fav_hotel_room(
        cls, 
        room_id: int,
        user_id: int|None = None,
        anonimous_id: str|None = None,
    ):
        if user_id:
            room_query = (select(Favourites)
                    .filter_by(user_id=user_id, room_id=room_id)
            )

            stmt_like = (insert(Favourites)
                    .values(user_id=user_id,
                            room_id=room_id)
                    .returning(Favourites.room_id,
                            Favourites.user_id)
            )

            stmt_dislike = (delete(Favourites)
                        .filter_by(anonimous_id=anonimous_id, room_id=room_id)
                        .returning(Favourites.room_id)   
                            )
        else:
            room_query = (select(Favourites)
                    .filter_by(anonimous_id=anonimous_id, room_id=room_id)
            )

            stmt_like = (insert(Favourites)
                    .values(anonimous_id=anonimous_id,
                            room_id=room_id)
                    .returning(Favourites.room_id,
                            Favourites.anonimous_id)
            )

            stmt_dislike = (delete(Favourites)
                        .filter_by(anonimous_id=anonimous_id, room_id=room_id)
                        .returning(Favourites.room_id)   
                            )
        
        async with async_session_maker() as session:
            room = await session.execute(room_query)
            room_res = room.mappings().all()
            if not room_res:
                res = await session.execute(stmt_like)
                await session.commit()
                return res.mappings().one()
            else:
                res = await session.execute(stmt_dislike)
                await session.commit()
                return res.mappings().one()

    
    
