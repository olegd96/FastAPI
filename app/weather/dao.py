import asyncio
from pydantic import TypeAdapter
from app.weather.schemas import Location, Weathers
from app.database import grpc_client
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorClient
from weather_pb2 import WeatherRequest # type: ignore
from app.loger import logger
from concurrent.futures import ThreadPoolExecutor as thread_executor

class WeatherDAO:
    """Data Access Object Layer for MongoDB"""

    @classmethod
    async def get_by_loc(
        cls,
        location: Location,
        db: AsyncIOMotorDatabase,
    ) -> Weathers| None:
        """
        Find city in MongoDB
        Args:
            location (Location): Location data model
            db (AsyncIOMotorDatabase)
        Returns:
            _type_: Weather data model or None
        """

        async def gloc():
            return await collection.find_one({"location": location.location})

        collection = db["weather"]
        task_loc = [asyncio.create_task(gloc())]
        loc, _ = await asyncio.wait(
            task_loc, timeout=0.5, return_when=asyncio.FIRST_COMPLETED
        )
        if loc:
            try:
                res = TypeAdapter(Weathers).validate_python(loc.pop().result())
            except:
                res = Weathers(
                    location="", temp=0.0, condition_text="", condition_img=""
                )
        else:
            res = Weathers(location="", temp=0.0, condition_text="", condition_img="")
        return res
    
    @classmethod
    async def grpc_get_by_loc(cls,
                                location:str) -> Weathers | None:
        result = None
        with thread_executor(max_workers=1) as executor:
            try:
                weather = executor.submit(
                    grpc_client.Weather, WeatherRequest(location=location)
                    )
                result = weather.result(timeout=0.2)
                if len(result.location) !=0:
                    result = TypeAdapter(Weathers).validate_python(result.location.pop())
            except (TimeoutError, Exception) as e:
                #weather.cancel()
                if isinstance(e, TimeoutError):
                    msg = "WeatherService Exc: TimeoutError"
                elif isinstance(e, Exception):
                    msg = "Unknown Exc"
                logger.error(msg, extra={"service": "WeatherService"}, exc_info=True)
        return result
        
