
from fastapi import APIRouter, Depends, Request, Response
from pydantic import TypeAdapter


from app.bookings.schemas import SNewBooking
from app.cart.schemas import SCart, SCartInfo
from app.cart.dao import CartDao
from app.users.dependencies import get_current_user
from app.exceptions import CannotAddToCart, CartBookMiss
from app.users.models import Users
import uuid

router = APIRouter(
    prefix="/cart",
    tags=["Корзина покупок"],
)

@router.post("", status_code=201)
async def add_book_to_cart(
    booking: SNewBooking,
    user: Users = Depends(get_current_user),
) -> SCartInfo:  
    booking_info = await CartDao.add(
    user_id=user.id,
    room_id=booking.room_id,
    date_from=booking.date_from,
    date_to=booking.date_to,
            )
    if not booking_info:
        raise CannotAddToCart
    return booking_info

@router.post("/anon", status_code=201)
async def add_book_to_anon_cart(
    booking: SNewBooking,
    request: Request,
    response: Response,
) -> SCartInfo:
    if not (anonimous_id := request.cookies.get("cart")):
        anonimous_id = str(uuid.uuid4())
        response.set_cookie("cart", anonimous_id, httponly=True)
    booking_info = await CartDao.add(
    room_id=booking.room_id,
    date_from=booking.date_from,
    date_to=booking.date_to,
    anonimous_id=anonimous_id,
            )
    if not booking_info:
        raise CannotAddToCart
    return booking_info

@router.get("")
async def get_books_from_cart(
    user: Users =  Depends(get_current_user)
) -> list[SCart]:
    bookings = await CartDao.find_all_with_images(user_id=user.id)
    return bookings

# @router.delete("/clear_cart")
# async def clear(days: int):
#     res = await CartDao.delete_old_book_from_cart(days)
#     return {'message': "successfully cleaning"}

@router.delete("/{booking_id}")
async def delete_book_from_cart(
    booking_id: int,
    user: Users = Depends(get_current_user)
):
    res = await CartDao.delete(booking_id=booking_id, user_id=user.id)
    if not res:
        raise CartBookMiss
    return res

@router.delete("/anon/{booking_id}")
async def delete_book_from_anon_cart(
    booking_id: int,
    request: Request,
):
    anonimous_id = request.cookies.get("cart")
    res = await CartDao.delete(booking_id=booking_id, anonimous_id=anonimous_id)
    if not res:
        raise CartBookMiss
    return res
