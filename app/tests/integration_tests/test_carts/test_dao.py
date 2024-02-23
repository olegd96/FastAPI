from datetime import datetime
import pytest

from app.cart.dao import CartDao


@pytest.mark.parametrize("room_id, date_from, date_to, anonimous_id, user_id", [
    (1, "2030-06-15", "2030-06-20", "", 1),
    (2, "2030-06-15", "2030-06-20", "", 2),
    (3, "2030-06-15", "2030-06-20", "", 2),
])

async def test_cart_crud(room_id, date_from , date_to, anonimous_id, user_id):
    new_cart = await CartDao.add(
            room_id=room_id,
            date_from=datetime.strptime(date_from, "%Y-%m-%d"),
            date_to=datetime.strptime(date_to, "%Y-%m-%d"),
            anonimous_id=anonimous_id,
            user_id=user_id,
    )

    assert new_cart.room_id == room_id
    assert new_cart.user_id == user_id

    user_cart = await CartDao.find_all_with_images(user_id=user_id)
    assert user_cart is not None  

    new_cart = await CartDao.find_one_or_none(id=new_cart.id)
    assert new_cart is not None

    deleted_cart = await CartDao.delete(
        booking_id=new_cart.id,
        user_id=user_id)
    assert deleted_cart is not None