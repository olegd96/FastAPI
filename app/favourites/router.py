

import uuid
from fastapi import APIRouter, Depends, Response, Request
from pydantic import TypeAdapter

from app.favourites.dao import FavDao
from app.favourites.schemas import  SFavList, SFavNew, SFav
from app.users.dependencies import get_current_user
from app.users.models import Users


router = APIRouter(
    prefix="/fav",
    tags=["Избранное"],
)

@router.post("", status_code=201)
async def check_fav(
    room: SFavNew,
    user: Users = Depends(get_current_user),
    ):
    res = await FavDao.check_fav_hotel_room(room_id=room.id, hotel_id=room.h_id, user_id=user.id)
    return res

@router.get("")
async def get_all_fav(
    user: Users = Depends(get_current_user)
) -> list[SFav]:
    res = await FavDao.find_all(user_id=user.id)
    return res

@router.post("/anon", status_code=201)
async def check_fav_anon(
    request: Request,
    response: Response,
    room: SFavNew,
    ):
    if not (anonimous_id := request.cookies.get("cart")):
        anonimous_id = str(uuid.uuid4())
        response.set_cookie("cart", anonimous_id, httponly=True)
    res = await FavDao.check_fav_hotel_room(room_id=room.id, hotel_id=room.h_id, anonimous_id=anonimous_id)
    return res

@router.get("/anon")
async def get_all_fav_anon(
    request: Request,
    response: Response,
) -> list[SFav]:
    if not (anonimous_id := request.cookies.get("cart")):
        anonimous_id = str(uuid.uuid4())
        response.set_cookie("cart", anonimous_id, httponly=True)
    res = await FavDao.find_all(anonimous_id=anonimous_id)
    return res

@router.get("/fav_list")
async def get_fav_list(
    user: Users = Depends(get_current_user),
) -> list[SFavList]:
    res = await FavDao.get_all_fav(user_id=user.id)
    return res


@router.get("/anon_fav_list")
async def get_anon_fav_list(
    request: Request,
    response: Response,
) -> list[SFavList]:
    if not (anonimous_id := request.cookies.get("cart")):
        anonimous_id = str(uuid.uuid4())
        response.set_cookie("cart", anonimous_id, httponly=True)
    res = await FavDao.get_all_fav(anonimous_id=anonimous_id)
    return res