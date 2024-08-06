from httpx import AsyncClient
import pytest

@pytest.mark.parametrize("room_id, date_from, date_to, rooms_in_cart, status_code", [
    (1, "2030-05-01", "2030-05-15", 1, 201),     
    (2, "2030-05-01", "2030-05-15", 2, 201),
    (3, "2030-05-01", "2030-05-15", 3, 201),
    (1, "2030-05-01", "2030-05-15", 4, 201),
    (2, "2030-05-01", "2030-05-15", 5, 201),
    (3, "2030-05-01", "2030-05-15", 6, 201),
])
async def test_add_and_get_cart(
    room_id, 
    date_from, 
    date_to,
    rooms_in_cart, 
    status_code,
    authenticated_ac: AsyncClient):
    response = await authenticated_ac.post("cart", json={
        "room_id": room_id,
        "date_from": date_from,
        "date_to": date_to
    })

    assert response.status_code == status_code

    response = await authenticated_ac.get("/cart")

    assert len(response.json()) == rooms_in_cart

async def test_get_and_delete_cart(authenticated_ac: AsyncClient):
    response = await authenticated_ac.get("/cart")

    assert response.status_code == 200 and len(response.json()) == 6

    for i in range(len(response.json())):
        await authenticated_ac.delete(f"cart/{response.json()[i]['id']}")

    response = await authenticated_ac.get("/cart")

    assert response.status_code == 200 and len(response.json()) == 0