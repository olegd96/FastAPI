from motor.motor_asyncio import AsyncIOMotorDatabase
from app.weather.schemas import Location, Weather
from app.weather.dao import WeatherDAO
from app.database import database_mongo, grpc_client
from app.weather_pb2 import WeatherRequest
from pydantic import TypeAdapter


class WeatherService:
    @classmethod
    async def get_weather(
        cls, location: str, db: AsyncIOMotorDatabase = database_mongo
    ) -> Weather | None:
        weather = await WeatherDAO.get_by_loc(Location(location=location), db=db)
        return weather
    
    @classmethod
    async def grpc_get_weather(cls, location: str
    ) -> Weather | None:
        weather = grpc_client.Weather(WeatherRequest(location=location))
        print(weather.location[0])
        return TypeAdapter(Weather).validate_python(weather.location.pop())
    

