import uuid
from sqlalchemy import JSON, Boolean, Computed, Date, ForeignKey, Integer, Column, String, text
from sqlalchemy.orm import mapped_column, Mapped, relationship
from app.database import Base
from datetime import date, datetime

class Bookings(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"))
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    date_from: Mapped[date] = mapped_column(Date)
    date_to: Mapped[date] = mapped_column(Date)
    price: Mapped[int]
    total_cost: Mapped[int] = mapped_column(Computed("(date_to - date_from) * price"))
    total_days: Mapped[int] = mapped_column(Computed("date_to - date_from"))
    deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    created: Mapped[datetime] = mapped_column(server_default=text("TIMEZONE('utc', now())"))
    rate: Mapped[int] = mapped_column(Integer, default=0)

    user: Mapped["Users"] = relationship(back_populates="bookings")
    room: Mapped["Rooms"] = relationship(back_populates="bookings")
   

    def __str__(self):
        return f"Бронирование #{self.id}"