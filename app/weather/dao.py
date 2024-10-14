import asyncio
from pydantic import TypeAdapter
from app.weather.schemas import Location, Weathers

from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorClient


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
