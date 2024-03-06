
from pydantic import TypeAdapter
from app.dao.base import BaseDAO
from app.users.models import RefreshSessionModel, Users
from app.database import async_session_maker
from sqlalchemy import select
from sqlalchemy.orm import load_only

from app.users.schemas import SUser

class UsersDAO(BaseDAO):
   models = Users

   @classmethod
   async def find_all(cls):
      async with async_session_maker() as session:
         query = select(cls.models.__table__.columns).options(load_only(
            Users.id, Users.email, Users.fio, Users.telephone,
            Users.is_active, Users.is_verified, Users.is_administrator
         ))
         result = await session.execute(query)
         result = result.mappings().all()
         
         return result
         
   @classmethod
   async def find_one_or_none(cls, **filter_by):
      async with async_session_maker() as session:
         query = (select(cls.models.__table__.columns)
         .filter_by(**filter_by)
         .options(load_only(
            Users.id, Users.email, Users.fio, Users.telephone,
            Users.is_active, Users.is_verified, Users.is_administrator
         ))
         )
         result = await session.execute(query)
         return result.mappings().one_or_none()


class RefreshSessionDAO(BaseDAO):
   models = RefreshSessionModel


               
