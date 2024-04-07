from sqlalchemy import JSON, Float, ForeignKey, Integer, Column, String
from sqlalchemy.orm import mapped_column, Mapped, relationship
from app.database import Base


class Hotels(Base):
    __tablename__ = "hotels"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str]
    location: Mapped[str]
    services: Mapped[list[str]] = mapped_column(JSON)
    rooms_quantity: Mapped[int]
    image_id: Mapped[int]
    #rate: Mapped[float] = mapped_column(Float, default=0)

    rooms: Mapped[list["Rooms"]] = relationship(back_populates="hotel")
    favourite: Mapped[list["Favourites"]] = relationship(back_populates="hotel")

    def __str__(self):
        return f"Отель {self.name} {self.location}"

    

