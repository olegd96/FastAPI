from datetime import date, datetime
import re
from typing import Annotated
import uuid
from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.bookings.dao import BookingDAO
from app.bookings.schemas import SBookingInfo
from app.cart.dao import CartDao
from app.exceptions import IncorrectTokenFormatException, TokenExpiredException, UserIsNotPresentException
from app.favourites.dao import FavDao
from app.hotels.dao import HotelsDAO
from app.hotels.rooms.dao import RoomsDAO
from app.cart.dao import CartDao
from app.pages.dependencies import check_valid_request
from app.users.dao import UsersDAO
from app.users.dependencies import get_current_user
from app.users.models import Users



from app.users.models import Users

router = APIRouter(
    prefix="/pages",
    tags=["Фронтенд"]
)

templates = Jinja2Templates(directory="app/templates")

@router.get("/clear", response_class=HTMLResponse)
async def clear_page(request: Request):
    return templates.TemplateResponse("clear.html", {"request": request})

@router.get("", response_class=HTMLResponse)
async def start_page(
    request: Request,
    ):
    len_cart = 0
    len_fav = 0
    if (anonimous_id := request.cookies.get("cart")):   
        len_cart = len(await CartDao.find_all_with_images(anonimous_id=anonimous_id))
        len_fav = len(await FavDao.find_all(anonimous_id=anonimous_id))
    return templates.TemplateResponse("index.html", {"request": request, "cart_count": len_cart, "fav_count": len_fav})

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, valid = Depends(check_valid_request)):
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/reg_user", response_class=HTMLResponse)
async def reg_user(request: Request, valid = Depends(check_valid_request)):
    return templates.TemplateResponse("register.html", {"request": request})


@router.get("/bookings", response_class=HTMLResponse)
async def booking_page(
    request: Request,
    valid = Depends(check_valid_request),
    user: Users = Depends(get_current_user),
    ):
    len_fav = len(await FavDao.find_all(user_id=user.id))    
    len_bookings = len(await BookingDAO.find_all_with_images(user_id=user.id))
    len_cart = len(await CartDao.find_all_with_images(user_id=user.id)) 
    return templates.TemplateResponse("booking.html", {"request": request, "user": user.email, "book_count": len_bookings, "cart_count": len_cart, "fav_count": len_fav})

    
@router.get("/anon_bookings", response_class=HTMLResponse)
async def anon_booking_page(
    request: Request,
    response: Response,
    valid = Depends(check_valid_request),
    ):
        if not (anonimous_id := request.cookies.get("cart")):
            anonimous_id = str(uuid.uuid4())
            response.set_cookie("cart", anonimous_id, httponly=True)
        len_fav = len(await FavDao.find_all(anonimous_id=anonimous_id))    
        len_cart = len(await CartDao.find_all_with_images(anonimous_id=anonimous_id)) 
        return templates.TemplateResponse("anon_booking.html", {"request": request, "cart_count": len_cart, "fav_count": len_fav})


@router.get("/my_bookings", response_class=HTMLResponse)
async def my_bookings(
    request: Request,
    valid = Depends(check_valid_request),
    user: Users = Depends(get_current_user),
    ):
    res = await BookingDAO.find_all_with_images(user_id=user.id)
    return templates.TemplateResponse("my_bookings.html", {"request": request, "bookings": res})


@router.get("/hotels", response_class=HTMLResponse)
async def get_hotels_by_loc_date(request: Request,
    location: str, date_from: date, date_to: date,
    valid = Depends(check_valid_request),
    ):
    res = await HotelsDAO.find_all(location, date_from, date_to)
    return templates.TemplateResponse("hotels_by_loc_and_time.html", {"request": request, "hotels": res})


@router.get("/hotel/id/{hotel_id}", response_class=HTMLResponse)
async def get_hotel_by_id(
    request: Request,
    hotel_id: int,
    valid = Depends(check_valid_request),
):  
    res = await HotelsDAO.find_one_or_none(id=hotel_id)
    return templates.TemplateResponse("hotel.html", {"request": request, "hotel": res})


@router.get("/search", response_class=HTMLResponse)
async def search_page(request: Request, valid = Depends(check_valid_request)):
    return templates.TemplateResponse("search_hotels.html", {"request": request})


@router.get("/hotels/{hotel_id}/rooms", response_class=HTMLResponse)
async def get_rooms_by__date(
    request: Request,
    response: Response,
    hotel_id: int, 
    date_from: date, 
    date_to: date,
    valid = Depends(check_valid_request),
    ):
    fav = []
    if (user_id := request.cookies.get("user_id")):
        fav = await FavDao.find_all(user_id=uuid.UUID(user_id))
    else:
        if not (anonimous_id := request.cookies.get("cart")):
            anonimous_id = str(uuid.uuid4())
            response.set_cookie("cart", anonimous_id, httponly=True)
        fav = await FavDao.find_all(anonimous_id=anonimous_id)
    fav = [f.room_id for f in fav]
    res = await RoomsDAO.find_all(hotel_id, date_from, date_to)
    return templates.TemplateResponse("rooms_by__time.html", {"request": request, "rooms": res, "fav": fav})

    
@router.get("/cart", response_class=HTMLResponse)
async def get_my_cart(
    request: Request,
    valid = Depends(check_valid_request),
    user: Users = Depends(get_current_user),
    ):
    res = await CartDao.find_all_with_images(user_id=user.id)
    fav = await FavDao.find_all(user_id=user.id)
    fav = [f.room_id for f in fav]
    return templates.TemplateResponse("my_cart.html", {"request": request, "bookings": res, "date": datetime.now().date(), "fav": fav})


@router.get("/cart/anon", response_class=HTMLResponse)
async def get_anon_cart(
    request: Request,
    response: Response,
    valid = Depends(check_valid_request),
    ):
    if not (anonimous_id := request.cookies.get("cart")):
        anonimous_id = str(uuid.uuid4())
        response.set_cookie("cart", anonimous_id, httponly=True)
    res = await CartDao.find_all_with_images(anonimous_id=anonimous_id)
    return templates.TemplateResponse("anon_cart.html", {"request": request, "bookings": res, "date": datetime.now().date()})


@router.get("/my_fav", response_class=HTMLResponse)
async def get_my_fav(
    request: Request,
    valid = Depends(check_valid_request),
    user: Users = Depends(get_current_user),
):
    res = await FavDao.get_all_fav(user_id=user.id)
    return templates.TemplateResponse("all_my_fav.html", {"request": request, "rooms": res})


@router.get("/anon_fav", response_class=HTMLResponse)
async def get_anon_fav(
    request: Request,
    response: Response,
    valid = Depends(check_valid_request),
):
    #check_valid_request(request=request)
    if not (anonimous_id := request.cookies.get("cart")):
        anonimous_id = str(uuid.uuid4())
        response.set_cookie("cart", anonimous_id, httponly=True)
    res = await FavDao.get_all_fav(anonimous_id=anonimous_id)
    return templates.TemplateResponse("all_anon_fav.html", {"request": request, "rooms": res})


@router.get("/fav_by_date")
async def get_fav_by_date(
    request: Request,
    date_from: date,
    date_to: date,
    valid = Depends(check_valid_request),
    user: Users = Depends(get_current_user),
):
    res = await FavDao.get_fav_by_date(date_from, date_to, user_id=user.id)
    return templates.TemplateResponse("all_my_fav_by_date.html", {"request": request, "rooms": res})

@router.get("/anon_fav_by_date", response_class=HTMLResponse)
async def get_anon_fav_by_date(
    request: Request,
    response: Response,
    date_from: date,
    date_to: date,
    valid = Depends(check_valid_request),
):
    if not (anonimous_id := request.cookies.get("cart")):
        anonimous_id = str(uuid.uuid4())
        response.set_cookie("cart", anonimous_id, httponly=True)
    res = await FavDao.get_fav_by_date(date_from, date_to, anonimous_id=anonimous_id)
    return templates.TemplateResponse("all_my_fav_by_date.html", {"request": request, "rooms": res})

@router.get("/personal_account", response_class=HTMLResponse)
async def personal_account(
    request: Request,
    valid = Depends(check_valid_request),
    user: Users = Depends(get_current_user),
):
    return templates.TemplateResponse("personal_account.html", {"request": request, "user": user.email})


@router.get("/personal_account_archive", response_class=HTMLResponse)
async def personal_account_archive(
    request: Request,
    valid = Depends(check_valid_request),
    user: Users = Depends(get_current_user),
):  
    past_bookings = await BookingDAO.find_all_past_bookings(user=user)
    fav = await FavDao.find_all(user_id=user.id)
    fav = [f.room_id for f in fav]
    return templates.TemplateResponse("personal_account_archive.html", {"request": request, "past_book": past_bookings, "fav": fav})

@router.get("/personal_account_archive_by_date", response_class=HTMLResponse)
async def personal_account_by_date(
    request: Request,
    date_from: date,
    date_to: date,
    valid = Depends(check_valid_request),
    user: Users = Depends(get_current_user),
):  
    past_bookings_by_date = await BookingDAO.find_all_past_bookings_by_date(
        user=user, 
        date_from=date_from,
        date_to=date_to)
    return templates.TemplateResponse("personal_account_archive_by_date.html", {"request": request, "past_book": past_bookings_by_date})

@router.get("/loc_list", response_class=HTMLResponse)
async def get_loc_list(
    request: Request,
    location: str,
    valid = Depends(check_valid_request),
):  
    loc_list = await HotelsDAO.find_location(location=location)
    if len(loc_list) > 0:
        loc_list = [re.search(rf"([^,]*{location}[^,]*)", loc, re.IGNORECASE).group() for loc in loc_list]
    return templates.TemplateResponse("loc_list.html", {"request": request, "loc_list": set(loc_list)})


@router.get("/banners", response_class=HTMLResponse)
async def get_most_popular(
    request: Request,
    valid = Depends(check_valid_request),
):  

    popular_hotels = await BookingDAO.get_most_popular_location()
    return templates.TemplateResponse("popular.html", {"request": request, "rooms_hotels": popular_hotels})