from motor.motor_asyncio import AsyncIOMotorDatabase
from app.weather.schemas import Location, Weather
from app.weather.dao import WeatherDAO
from app.database import database_mongo, grpc_client
from app.weather_pb2 import WeatherRequest


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
        weather = await grpc_client.Weather(WeatherRequest(location))
        return Weather(location=location,
                       temp=weather.temp,
                       condition_text=weather.condition_text,
                       condition_img=weather.condition_img,
                    )
    

