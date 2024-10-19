from motor.motor_asyncio import AsyncIOMotorDatabase
from app.weather.schemas import Location, Weathers
from app.weather.dao import WeatherDAO
from app.database import database_mongo, grpc_client

from pydantic import TypeAdapter



class WeatherService:
    @classmethod
    async def get_weather(
        cls, location: str, db: AsyncIOMotorDatabase = database_mongo
    ) -> Weathers | None:
        weather = await WeatherDAO.get_by_loc(Location(location=location), db=db)
        return weather
    
    @classmethod
    async def grpc_get_weather(cls, location: str
    ) -> Weathers | None:
        weather = grpc_client.Weather(WeatherRequest(location=location))
        
        return None
