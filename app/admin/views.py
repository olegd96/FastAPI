from sqladmin import ModelView

from app.bookings.models import Bookings
from app.cart.models import Carts
from app.favourites.models import Favourites
from app.hotels.models import Hotels
from app.hotels.rooms.models import Rooms
from app.users.models import Users


class UsersAdmin(ModelView, model=Users):
    column_list = [Users.id, Users.email]
    can_delete = False
    name = "Пользователь"
    name_plural = "Пользователи"
    icon = "fa-solid fa-user"
    column_details_exclude_list = [Users.hashed_password]


class BookingsAdmin(ModelView, model=Bookings):
    column_list = [c.name for c in Bookings.__table__.c] + [Bookings.user]
    name = "Бронь"
    name_plural = "Брони"
    icon = "fa-solid fa-book"
    


class HotelsAdmin(ModelView, model=Hotels):
    column_list = [c.name for c in Hotels.__table__.c] + [Hotels.rooms]
    name = "Отель"
    name_plural = "Отели"
    icon = "fa-solid fa-hotel"


class RoomsAdmin(ModelView, model=Rooms):
    column_list = [c.name for c in Rooms.__table__.c] + [Rooms.hotel, Rooms.bookings]
    name = "Номер"
    name_plural = "Номера"
    icon = "fa-solid fa-bed"

class CartAdmin(ModelView, model=Carts):
    column_list = [c.name for c in Carts.__table__.c] + [Carts.user] + [Carts.room]
    name = "Корзина"
    name_plural = "Корзина"
    icon = "fa-solid fa-cart"

class FavourAdmin(ModelView, model=Favourites):
    column_list = [c.name for c in Favourites.__table__.c] + [Favourites.user] + [Favourites.room] + [Favourites.hotel]
    name = "Избранное"
    name_plural = "Избранное"
    icon = ""

    
    