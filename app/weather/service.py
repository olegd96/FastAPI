from motor.motor_asyncio import AsyncIOMotorDatabase
from app.weather.schemas import Location, Weather
from app.weather.dao import WeatherDAO
from app.database import database_mongo


class WeatherService():

    @classmethod
    async def get_weather(cls, location: str, db: AsyncIOMotorDatabase = database_mongo) -> Weather|None:
        weather = await WeatherDAO.get_by_loc(Location(location=location), db=db)
        return weather