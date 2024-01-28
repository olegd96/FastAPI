from app.cart.models import Carts
from app.bookings.dao import BookingDAO
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer

class CartDao(BookingDAO):
    models = Carts

    id: Mapped[int] = mapped_column(Integer, primary_key=True)