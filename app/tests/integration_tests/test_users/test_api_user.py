from fastapi.security import OAuth2PasswordRequestForm
from httpx import AsyncClient
import pytest


@pytest.mark.parametrize(
    "email, password, fio, status_code",
    [
        ("kot@pes.com", "kotopes", "kotopes", 200),
        ("kot@pes.com", "kot0pes", "kot0pes", 409),
        ("pes@kot.com", "kot0pes", "kot0pes", 200),
        ("abcde", "kjkhk", "kjkhk", 422),
    ],
)
async def test_register_user(email, password, fio, status_code, ac: AsyncClient):
    response = await ac.post(
        "auth/register",
        json={
            "email": email,
            "fio": fio,
            "telephone": " ",
            "is_active": True,
            "is_verified": False,
            "is_administrator": False,
            "password": password,
        },
    )

    assert response.status_code == status_code


@pytest.mark.parametrize(
    "email, password, status_code",
    [
        ("test@test.com", "test", 200),
        ("artem@example.com", "artem", 200),
        ("wrong_person@example.com", "wrong", 401),
    ],
)
async def test_login_user(email, password, status_code, ac: AsyncClient):
    response = await ac.post(
        "auth/login", data={"username": email, "password": password}
    )

    assert response.status_code == status_code
