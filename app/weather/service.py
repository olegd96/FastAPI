from motor.motor_asyncio import AsyncIOMotorDatabase
from app.weather.schemas import Location, Weathers
from app.weather.dao import WeatherDAO
from app.database import database_mongo, grpc_client
from weather_pb2 import WeatherRequest # type: ignore
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
        if len(weather.location) !=0:
            return TypeAdapter(Weathers).validate_python(weather.location.pop())
        return None
