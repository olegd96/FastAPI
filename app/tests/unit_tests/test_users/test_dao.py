from pydantic import TypeAdapter
from app.users.dao import Users, UsersDAO
import pytest
import uuid

from app.users.schemas import SUser, SUserBase

@pytest.mark.parametrize("user_id, email, is_present", [
    ("3ede3539-f445-44fc-a81a-d036672603b9", "test@test.com", True),
    ("3ede3539-f445-44fc-a81a-d036672603c8", "artem@example.com", True),
    ("3ede3539-f445-44fc-a81a-d036672604f8", ".....", False),
])
async def test_find_user_by_id(user_id, email, is_present):
    user = await UsersDAO.find_by_id(uuid.UUID(user_id))
    

    if is_present:

        assert user
        assert user.id == uuid.UUID(user_id)
        assert user.email == email
    else:
        assert not user