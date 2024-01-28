from datetime import date
from sqlalchemy import Integer, ForeignKey, Date, Computed
from app.database import Base
from sqlalchemy.orm import Mapped, relationship, mapped_column
from app.bookings.models import Bookings

class Carts(Base):

    __tablename__ = "cart"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    date_from: Mapped[date] = mapped_column(Date)
    date_to: Mapped[date] = mapped_column(Date)
    price: Mapped[int]
    total_cost: Mapped[int] = mapped_column(Computed("(date_to - date_from) * price"))
    total_days: Mapped[int] = mapped_column(Computed("date_to - date_from"))

    def __str__(self):
        return f"Бронирование #{self.id}"