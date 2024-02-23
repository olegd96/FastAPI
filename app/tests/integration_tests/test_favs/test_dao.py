from datetime import datetime
import pytest

from app.favourites.dao import FavDao

@pytest.mark.parametrize("room_id, hotel_id, user_id, anonimous_id, date_from , date_to", [
    (1, 1, 1, None, "2024-02-20", "2024-02-25"),
    (2, 1, 1, None, "2024-02-20", "2024-02-25"),
    (3, 2, 1, None, "2024-02-20", "2024-02-25"),
    (4, 2, 1, None, "2024-02-20", "2024-02-25"),
])

async def test_fav_crud(room_id, hotel_id, user_id, anonimous_id, date_from , date_to):
    new_fav = await FavDao.check_fav_hotel_room(
        room_id,
        hotel_id,
        user_id,
        anonimous_id)
    
    assert new_fav['room_id'] == room_id

    fav_list = await FavDao.get_all_fav(user_id=user_id)

    assert len(fav_list) == 1

    fav_list_by_date = await FavDao.get_fav_by_date(
        date_from=datetime.strptime(date_from, "%Y-%m-%d"),
        date_to=datetime.strptime(date_to, "%Y-%m-%d"),
        user_id=user_id
    )

    assert fav_list == fav_list_by_date

    new_fav = await FavDao.check_fav_hotel_room(
        room_id,
        hotel_id,
        user_id)
    
    assert new_fav['room_id'] == room_id

    fav_list = await FavDao.get_all_fav(user_id=user_id)

    assert len(fav_list) == 0