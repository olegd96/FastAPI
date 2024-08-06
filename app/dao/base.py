from typing import Any, Dict, Optional, TypeVar, Union
import uuid
from venv import logger
from pydantic import BaseModel
from sqlalchemy import insert, select, delete, update
from app.database import async_session_maker, Base
from sqlalchemy.exc import SQLAlchemyError


UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
ModelType = TypeVar("ModelType", bound=Base)

class BaseDAO:
    models = None


    @classmethod
    async def find_by_id(cls, model_id: int|uuid.UUID):
        async with async_session_maker() as session:
            query = select(cls.models).filter_by(id=model_id)
            result = await session.execute(query)
            return result.scalars().one_or_none()

    @classmethod
    async def find_one_or_none(cls, **filter_by):
        async with async_session_maker() as session:
            query = select(cls.models.__table__.columns).filter_by(**filter_by)
            result = await session.execute(query)
            return result.mappings().one_or_none()
        
    @classmethod
    async def find_all(cls, **filter_by):
        async with async_session_maker() as session:
            query = select(cls.models.__table__.columns).filter_by(**filter_by)
            result = await session.execute(query)
            return result.mappings().all()
        
    @classmethod
    async def add(cls, **data):
        try:
            async with async_session_maker() as session:
                query = insert(cls.models).values(**data).returning(cls.models.id)
                result = await session.execute(query)
                await session.commit()
                res = result.mappings().first()
                return res
        except (SQLAlchemyError, Exception) as e:
            if isinstance(e, SQLAlchemyError):
                msg = "Database Exc: Cannot insert data into table"
            elif isinstance(e, Exception):
                msg = "Unknown Exc: Cannot insert data into table"

            logger.error(msg, extra={"table": cls.models.__tablename__}, exc_info=True)
            return None



    @classmethod
    async def delete(cls, **filter_by):
        try:
            async with async_session_maker() as session:
                query = delete(cls.models).filter_by(**filter_by)
                await session.execute(query)
                await session.commit()
        except (SQLAlchemyError, Exception) as e:
            if isinstance(e, SQLAlchemyError):
                msg = "Database Exc: Cannot delete data from table"
            elif isinstance(e, Exception):
                msg = "Unknown Exc: Cannot delete data from table"

            logger.error(msg, extra={"table": cls.models.__tablename__}, exc_info=True)
            return None



    @classmethod
    async def add_bulk(cls, *data):
        try:
            query = insert(cls.models).values(*data).returning(cls.models.id)
            async with async_session_maker() as session:
                result = await session.execute(query)
                await session.commit()
                return result.mappings().first()
        except (SQLAlchemyError, Exception) as e:
            if isinstance(e, SQLAlchemyError):
                msg = "Database Exc: Cannot insert data into table"
            elif isinstance(e, Exception):
                msg = "Unknown Exc: Cannot insert data into table"

            logger.error(msg, extra={"table": cls.models.__tablename__}, exc_info=True)
            return None
        
    @classmethod
    async def update(cls, 
                    *where, 
                    data: Union[UpdateSchemaType, Dict[str, Any]]) -> Optional[ModelType]:
        if isinstance(data, dict):
            update_data = data
        else:
            update_data = data.model_dump(exclude_unset=True)
        try:
            stmt = (update(cls.models)
                    .where(*where)
                    .values(**update_data)
                    .returning(cls.models.__table__.columns))
            async with async_session_maker() as session:
                res = await session.execute(stmt)
                await session.commit()
                return res.mappings().one()
        except (SQLAlchemyError, Exception) as e:
            if isinstance(e, SQLAlchemyError):
                msg = "Database Exc: Cannot update data into table"
            elif isinstance(e, Exception):
                msg = "Unknown Exc: Cannot update data into table"

            logger.error(msg, extra={"table": cls.models.__tablename__}, exc_info=True)
            return None
                
                            