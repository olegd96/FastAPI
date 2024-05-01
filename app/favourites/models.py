import uuid
from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from app.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.hotels.models import Hotels
    from app.users.models import Users
    from app.hotels.rooms.models import Rooms


class Favourites(Base):

    __tablename__ = "favourites"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=True)
    anonimous_id: Mapped[str] = mapped_column(String, nullable=True)
    hotel_id: Mapped[int] = mapped_column(ForeignKey("hotels.id"), nullable=True)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"), nullable=True)

    user: Mapped["Users"] = relationship(back_populates="favourites")
    hotel: Mapped["Hotels"] = relationship(back_populates="favourite")
    room: Mapped["Rooms"] = relationship(back_populates="favourite")

    __table_args__ = (
        (UniqueConstraint("user_id", "room_id", name="fav_room_uc"),)
        )
    
    def __str__(self):
        return f"Отель {self.hotel_id}, комната {self.room_id}"

