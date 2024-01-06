

from httpx import AsyncClient
import pytest

@pytest.mark.parametrize("location, date_from, date_to, status_code, detail", [
        ("Алтай", "2030-07-25", "2030-06-20", 400, "Дата заезда не может быть позже даты выезда"),
        ("Алтай", "2030-07-25", "2030-09-20", 400, "Невозможно забронировать отель сроком более месяца"),
        ("Алтай", "2030-07-15", "2030-07-20", 200),

])
async def test_get_hotels(location, date_from, date_to, status_code, detail,
                          authenticated_ac: AsyncClient):
        response = await authenticated_ac.get(f"/hotels/{location}", params={
                "date_from": date_from,
                "date_to": date_to,
        })

        assert response.status_code == status_code
        if str(status_code).startswith("4"):
                assert response.json()["detail"] == detail
