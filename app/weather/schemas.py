from pydantic import BaseModel, ConfigDict


class Location(BaseModel):
    location: str

    model_config = ConfigDict(from_attributes=True)


class Weathers(Location):
    temp: float
    condition_text: str
    condition_img: str

    model_config = ConfigDict(from_attributes=True)
