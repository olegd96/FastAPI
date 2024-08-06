from typing import TYPE_CHECKING, Optional
from sqlalchemy import JSON, ForeignKey, Integer, Column, String
from sqlalchemy.orm import mapped_column, Mapped, relationship
from app.database import Base

if TYPE_CHECKING:
    from app.hotels.models import Hotels
    from app.favourites.models import Favourites
    from app.bookings.models import Bookings
    from app.cart.models import Carts 

class Rooms(Base):
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    hotel_id: Mapped[int] = mapped_column(ForeignKey("hotels.id"))
    name: Mapped[str]
    description: Mapped[Optional[str]]
    price: Mapped[int]
    services: Mapped[list[str]] = mapped_column(JSON)
    quantity: Mapped[int]
    image_id: Mapped[int]

    hotel: Mapped["Hotels"] = relationship(back_populates="rooms")
    bookings: Mapped[list["Bookings"]] = relationship(back_populates="room")
    carts: Mapped[list["Carts"]] = relationship(back_populates="room")
    favourite: Mapped[list["Favourites"]] = relationship(back_populates="room")

    def __str__(self):
        return f"Номер {self.name}"