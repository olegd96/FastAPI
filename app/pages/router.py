from datetime import date, datetime
import re
from typing import Annotated
import uuid
from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import TypeAdapter
from app.bookings.dao import BookingDAO
from app.bookings.models import Bookings
from app.bookings.schemas import SBookingInfo, SBookingRate
from app.cart.dao import CartDao
from app.exceptions import CannotBookHotelForLongPeriod, DateFromCannotBeAfterDateTo, IncorrectTokenFormatException, TokenExpiredException, UserIsNotPresentException
from app.favourites.dao import FavDao
from app.hotels.dao import HotelsDAO
from app.hotels.models import Hotels
from app.hotels.rooms.dao import RoomsDAO
from app.cart.dao import CartDao
from app.pages.dependencies import check_valid_request
from app.users.dao import UsersDAO
from app.users.dependencies import get_current_user
from app.users.models import Users



from app.users.models import Users
from app.weather.schemas import Location, Weather
from app.weather.service import WeatherService
from app.config import settings

router = APIRouter(
    prefix="/pages",
    tags=["Фронтенд"]
)

templates = Jinja2Templates(directory="app/templates")


@router.get("", response_class=HTMLResponse)
async def start_page(
    request: Request,
    response: Response,
    ):
    len_cart = 0
    len_fav = 0
    if not (anonimous_id := request.cookies.get("cart")):
            anonimous_id = str(uuid.uuid4())
            response.set_cookie("cart", anonimous_id, httponly=True)
    len_cart = len(await CartDao.find_all_with_images(anonimous_id=anonimous_id))
    len_fav = len(await FavDao.find_all(anonimous_id=anonimous_id))
    return templates.TemplateResponse("index.html", {"request": request, "cart_count": len_cart, "fav_count": len_fav, "ids":anonimous_id, "s3": settings.S3_PREFIX})

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
    return templates.TemplateResponse("my_bookings.html", {"request": request, "bookings": res, "s3": settings.S3_PREFIX})


@router.get("/hotels", response_class=HTMLResponse)
async def get_hotels_by_loc_date(request: Request,
    location: str, date_from: date, date_to: date, limit: int = 3, offset: int = 0,
    valid = Depends(check_valid_request),
    ):
    if date_from > date_to:
        raise DateFromCannotBeAfterDateTo
    if (date_to - date_from).days > 31:
        raise CannotBookHotelForLongPeriod
    res = await HotelsDAO.find_all(location, date_from, date_to, limit, offset)
    count = await HotelsDAO.hotels_count(location, date_from, date_to)
    if location:
        weather = await WeatherService.get_weather(location)
    else:
        weather = Weather(location='', temp=0, condition_text='', condition_img='')
    return templates.TemplateResponse("hotels_by_loc_and_time.html", {"request": request, "hotels": res, "offset": offset, "count": count, 'weather': weather, "s3": settings.S3_PREFIX})


@router.get("/hotel/id/{hotel_id}", response_class=HTMLResponse)
async def get_hotel_by_id(
    request: Request,
    hotel_id: int,
    valid = Depends(check_valid_request),
):  
    res = await HotelsDAO.find_one_or_none(id=hotel_id)
    return templates.TemplateResponse("hotel.html", {"request": request, "hotel": res, "s3": settings.S3_PREFIX})


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
    if date_from > date_to:
        raise DateFromCannotBeAfterDateTo
    if (date_to - date_from).days > 31:
        raise CannotBookHotelForLongPeriod
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
    return templates.TemplateResponse("rooms_by__time.html", {"request": request, "rooms": res, "fav": fav, "s3": settings.S3_PREFIX})

    
@router.get("/cart", response_class=HTMLResponse)
async def get_my_cart(
    request: Request,
    valid = Depends(check_valid_request),
    user: Users = Depends(get_current_user),
    ):
    res = await CartDao.find_all_with_images(user_id=user.id)
    fav = await FavDao.find_all(user_id=user.id)
    fav = [f.room_id for f in fav]
    return templates.TemplateResponse("my_cart.html", {"request": request, "bookings": res, "date": datetime.now().date(), "fav": fav, "s3": settings.S3_PREFIX})


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
    return templates.TemplateResponse("anon_cart.html", {"request": request, "bookings": res, "date": datetime.now().date(), "s3": settings.S3_PREFIX})


@router.get("/my_fav", response_class=HTMLResponse)
async def get_my_fav(
    request: Request,
    limit: int = 3,
    offset: int = 0,
    valid = Depends(check_valid_request),
    user: Users = Depends(get_current_user),
):
    res = await FavDao.get_all_fav(limit, offset, user_id=user.id)
    count = await FavDao.count_all_fav(user_id = user.id)
    return templates.TemplateResponse("all_my_fav.html", {"request": request, "rooms": res, "offset": offset, "count": count, "s3": settings.S3_PREFIX})


@router.get("/my_fav_next", response_class=HTMLResponse)
async def get_my_fav(
    request: Request,
    limit: int = 3,
    offset: int = 0,
    valid = Depends(check_valid_request),
    user: Users = Depends(get_current_user),
):
    res = await FavDao.get_all_fav(limit, offset, user_id=user.id)
    count = await FavDao.count_all_fav(user_id = user.id)
    return templates.TemplateResponse("next_my_fav.html", {"request": request, "rooms": res, "offset": offset, "count": count, "s3": settings.S3_PREFIX})


@router.get("/anon_fav", response_class=HTMLResponse)
async def get_anon_fav(
    request: Request,
    response: Response,
    limit: int = 3,
    offset: int = 0,
    valid = Depends(check_valid_request),
):
    if not (anonimous_id := request.cookies.get("cart")):
        anonimous_id = str(uuid.uuid4())
        response.set_cookie("cart", anonimous_id, httponly=True)
    res = await FavDao.get_all_fav(limit, offset, anonimous_id=anonimous_id)
    count = await FavDao.count_all_fav(anonimous_id=anonimous_id)
    return templates.TemplateResponse("all_anon_fav.html", {"request": request, "rooms": res, "offset": offset, "count": count, "s3": settings.S3_PREFIX})


@router.get("/anon_fav_next", response_class=HTMLResponse)
async def get_my_fav(
    request: Request,
    response: Response,
    limit: int = 3,
    offset: int = 0,
    valid = Depends(check_valid_request),
):
    if not (anonimous_id := request.cookies.get("cart")):
        anonimous_id = str(uuid.uuid4())
        response.set_cookie("cart", anonimous_id, httponly=True)
    res = await FavDao.get_all_fav(limit, offset, anonimous_id=anonimous_id)
    count = await FavDao.count_all_fav(anonimous_id=anonimous_id)
    return templates.TemplateResponse("next_anon_fav.html", {"request": request, "rooms": res, "offset": offset, "count": count, "s3": settings.S3_PREFIX})


@router.get("/fav_by_date")
async def get_fav_by_date(
    request: Request,
    date_from: date,
    date_to: date,
    valid = Depends(check_valid_request),
    user: Users = Depends(get_current_user),
):  
    if date_from > date_to:
        raise DateFromCannotBeAfterDateTo
    if (date_to - date_from).days > 31:
        raise CannotBookHotelForLongPeriod 
    res = await FavDao.get_fav_by_date(date_from, date_to, user_id=user.id)
    return templates.TemplateResponse("all_my_fav_by_date.html", {"request": request, "rooms": res, "s3": settings.S3_PREFIX})

@router.get("/anon_fav_by_date", response_class=HTMLResponse)
async def get_anon_fav_by_date(
    request: Request,
    response: Response,
    date_from: date,
    date_to: date,
    valid = Depends(check_valid_request),
):
    if date_from > date_to:
        raise DateFromCannotBeAfterDateTo
    if (date_to - date_from).days > 31:
        raise CannotBookHotelForLongPeriod
    if not (anonimous_id := request.cookies.get("cart")):
        anonimous_id = str(uuid.uuid4())
        response.set_cookie("cart", anonimous_id, httponly=True)
    res = await FavDao.get_fav_by_date(date_from, date_to, anonimous_id=anonimous_id)
    return templates.TemplateResponse("all_my_fav_by_date.html", {"request": request, "rooms": res, "s3": settings.S3_PREFIX})

@router.get("/personal_account", response_class=HTMLResponse)
async def personal_account(
    request: Request,
    valid = Depends(check_valid_request),
    user: Users = Depends(get_current_user),
):
    return templates.TemplateResponse("personal_account.html", {"request": request, "user": user})


@router.get("/personal_account_archive", response_class=HTMLResponse)
async def personal_account_archive(
    request: Request,
    limit: int = 3,
    offset: int = 0,
    valid = Depends(check_valid_request),
    user: Users = Depends(get_current_user),
):  
    past_bookings = await BookingDAO.find_all_past_bookings(user=user, limit=limit, offset=offset)
    count_past_bookings = await BookingDAO.count_all_past(user=user)
    fav = await FavDao.find_all(user_id=user.id)
    fav = [f.room_id for f in fav]
    return templates.TemplateResponse("personal_account_archive.html", 
                                      {"request": request, 
                                       "past_book": past_bookings, 
                                       "fav": fav, 
                                       "count": count_past_bookings,
                                       "offset": offset,
                                       "s3": settings.S3_PREFIX})

@router.get("/personal_account_archive_next", response_class=HTMLResponse)
async def personal_account_archive(
    request: Request,
    limit: int = 3,
    offset: int = 0,
    valid = Depends(check_valid_request),
    user: Users = Depends(get_current_user),
):  
    past_bookings = await BookingDAO.find_all_past_bookings(user=user, limit=limit, offset=offset)
    count_past_bookings = await BookingDAO.count_all_past(user=user)
    fav = await FavDao.find_all(user_id=user.id)
    fav = [f.room_id for f in fav]
    return templates.TemplateResponse("personal_account_archive_next.html", 
                                      {"request": request, 
                                       "past_book": past_bookings, 
                                       "fav": fav, 
                                       "count": count_past_bookings,
                                       "offset": offset,
                                       "s3": settings.S3_PREFIX})


@router.get("/personal_account_archive_by_date", response_class=HTMLResponse)
async def personal_account_by_date(
    request: Request,
    date_from: date,
    date_to: date,
    valid = Depends(check_valid_request),
    user: Users = Depends(get_current_user),
):  
    if date_from > date_to:
        raise DateFromCannotBeAfterDateTo
    if (date_to - date_from).days > 31:
        raise CannotBookHotelForLongPeriod
    past_bookings_by_date = await BookingDAO.find_all_past_bookings_by_date(
        user=user, 
        date_from=date_from,
        date_to=date_to)
    fav = await FavDao.find_all(user_id=user.id)
    fav = [f.room_id for f in fav]
    return templates.TemplateResponse("personal_account_archive_by_date.html", {"request": request, "past_book": past_bookings_by_date, "fav": fav, "s3": settings.S3_PREFIX})

@router.get("/loc_list", response_class=HTMLResponse)
async def get_loc_list(
    request: Request,
    location: str,
    valid = Depends(check_valid_request),
):  
    loc_list = await HotelsDAO.find_location(location=location)
    # if len(loc_list) > 0:
    #     loc_list = [re.search(rf"([^,]*{location}[^,]*)", loc, re.IGNORECASE).group() for loc in loc_list]
    return templates.TemplateResponse("loc_list.html", {"request": request, "loc_list": set(loc_list)})


@router.get("/banners", response_class=HTMLResponse)
async def get_most_popular(
    request: Request,
    valid = Depends(check_valid_request),
):  

    popular_hotels = await BookingDAO.get_most_popular_location()
    return templates.TemplateResponse("popular.html", {"request": request, "rooms_hotels": popular_hotels, "s3": settings.S3_PREFIX})


@router.get("/editor", response_class=HTMLResponse)
async def get_editor(
    request: Request,
    user: Users = Depends(get_current_user)
):
    return templates.TemplateResponse("edit_personal.html", {"request": request, "user": user})

@router.get("/edit_pass", response_class=HTMLResponse)
async def get_edit_pass(
    request: Request,
    user: Users = Depends(get_current_user)
):
    return templates.TemplateResponse("change_password.html", {"request": request})

@router.get("/chat", response_class=HTMLResponse)
async def get_chat(
    request: Request,
):
    return templates.TemplateResponse("ws.html", {"request": request})

@router.post("/rate", response_class=HTMLResponse)
async def get_rate(
    request: Request,
    data: SBookingRate,
    user: Users = Depends(get_current_user),
):
    data = data.model_dump()
    rate = await BookingDAO.update(Bookings.id==int(data['ids']),  data={"rate": int(data['rate'])})
    hotel_rate = await BookingDAO.set_avg_by_room_id(room_id=rate.room_id)
    return templates.TemplateResponse("rate.html", {"request": request, "book": rate})