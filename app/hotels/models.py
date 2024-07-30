from typing import TYPE_CHECKING, Annotated
from sqlalchemy import JSON, Float, ForeignKey, Integer, Column, Null, String, Index
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import TSVECTOR
from app.database import Base

  
from app.hotels.rooms.models import Rooms
from app.favourites.models import Favourites



class Hotels(Base):
    __tablename__ = "hotels"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str]
    city: Mapped[str] = mapped_column(String, default="")
    location: Mapped[str]
    services: Mapped[list[str]] = mapped_column(JSON)
    rooms_quantity: Mapped[int]
    image_id: Mapped[int]
    rate: Mapped[float] = mapped_column(Float, default=0)
    tsv : Mapped[dict] = mapped_column(TSVECTOR, nullable=True, server_onupdate=func.to_tsvector('russian', city))

    rooms: Mapped[list["Rooms"]] = relationship(back_populates="hotel")
    favourite: Mapped[list["Favourites"]] = relationship(back_populates="hotel")

    def __str__(self):
        return f"Отель {self.name} {self.location}"
    
    __table_args__ = (
        Index('ts_city', 'tsv', postgresql_using = 'gin'),
    )

