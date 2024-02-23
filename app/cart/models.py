from datetime import date, datetime
import uuid
from sqlalchemy import Boolean, Integer, ForeignKey, Date, Computed, String, text
from app.database import Base
from sqlalchemy.orm import Mapped, relationship, mapped_column
from app.bookings.models import Bookings

class Carts(Base):

    __tablename__ = "carts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"))
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=True)
    anonimous_id: Mapped[str] = mapped_column(String, nullable=True)
    date_from: Mapped[date] = mapped_column(Date)
    date_to: Mapped[date] = mapped_column(Date)
    price: Mapped[int]
    total_cost: Mapped[int] = mapped_column(Computed("(date_to - date_from) * price"))
    total_days: Mapped[int] = mapped_column(Computed("date_to - date_from"))
    deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    created: Mapped[datetime] = mapped_column(server_default=text("TIMEZONE('utc', now())"))

    user: Mapped["Users"] = relationship(back_populates="carts")
    room: Mapped["Rooms"] = relationship(back_populates="carts")


    def __str__(self):
        return f"Бронирование #{self.id}"