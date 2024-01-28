

from fastapi import APIRouter, Depends
from pydantic import TypeAdapter

from app.bookings.schemas import SNewBooking
from app.cart.dao import CartDao
from app.users.dependencies import get_current_user
from app.exceptions import CannotAddToCart
from app.users.models import Users


router = APIRouter(
    prefix="/cart",
    tags=["Корзина покупок"],
)

@router.post("", status_code=201)
async def add_book_to_cart(
    booking: SNewBooking,
    user: Users = Depends(get_current_user),
):
    booking = await CartDao.add(
        user_id=user.id,
        room_id=booking.room_id,
        date_from=booking.date_from,
        date_to=booking.date_to,
                )
    if not booking:
        raise CannotAddToCart
    return booking

@router.get("")
async def get_books_from_cart(
    user: Users =  Depends(get_current_user)
):
    bookings = await CartDao.find_all_with_images(user_id=user.id)
    return bookings

@router.delete("/{booking_id}")
async def delete_book_from_cart(
    booking_id: int,
    user: Users = Depends(get_current_user)
):
    res = await CartDao.delete(booking_id=booking_id, user_id=user.id)
    return res