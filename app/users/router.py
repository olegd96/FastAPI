
from typing import List
import uuid
from fastapi import APIRouter, Depends, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import TypeAdapter
from app.cart.dao import CartDao
from app.exceptions import CannotAddDataToDatabase, IncorrectCurrentPasswordException, IncorrectEmailOrPasswordException, InvalidTokenException, PasswordNotConfirm, UnverifiedEmailException, UserAlreadyExistsException
from app.favourites.dao import FavDao
from app.tasks.tasks import send_registration_confirmation_email
from app.users.dao import  UsersDAO
from app.users.utils import get_password_hash
from app.users.dependencies import get_current_admin_user, get_current_user
from app.users.models import Users
from app.config import settings

from app.users.schemas import SToken, SUser, SUserDB, SUserReAuth, SUserReg, SUserUpdate, SUserVerify
from app.users.service import AuthService

router_users = APIRouter(
    prefix="/auth",
    tags=["Auth & Пользователи"],
)

router_auth = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)


@router_auth.post("/register")
async def register_user(user: SUserReg):
    existing_user = await UsersDAO.find_one_or_none(email=user.email)
    if existing_user:
        raise UserAlreadyExistsException
    user.is_verified = False
    user.is_administrator = False
    hashed_password = get_password_hash(user.password)
    # user_db = SUserDB(
    #     **user.model_dump(),
    #     hashed_password=hashed_password).model_dump()
    new_user = await UsersDAO.add(
        **SUserDB(
            **user.model_dump(),
            hashed_password=hashed_password).model_dump())
    if not new_user:
        raise CannotAddDataToDatabase
    send_registration_confirmation_email.delay(new_user.id,
                                               user.email,
                                               )
    return new_user


@router_auth.post("/login")
async def login_user(request: Request, response: Response,
                     credentials: OAuth2PasswordRequestForm = Depends())  -> SToken:
    user = await AuthService.authenticate_user(credentials.username, credentials.password)
    if not user:
        raise IncorrectEmailOrPasswordException
    if not user.is_verified:
        raise UnverifiedEmailException
    token = await AuthService.create_token(user.id)
    response.set_cookie("booking_access_token",
                        token.access_token,
                        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                        httponly=True)
    response.set_cookie("booking_refresh_token",
                        token.refresh_token,
                        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 30 * 24 * 60,
                        httponly=True)
    response.set_cookie("user_id", user.id, httponly=True)
    if (anonimous_id := request.cookies.get("cart")):
        res = await CartDao.from_anon_to_reg(anonimous_id=anonimous_id, user=user)
        res_1 = await FavDao.from_anon_to_reg(anonimous_id=anonimous_id, user=user)
    return token


@router_auth.post("/logout")
async def logout_user(
    request: Request,
    response: Response,
):
    response.delete_cookie("booking_access_token")
    response.delete_cookie("booking_refresh_token")
    response.delete_cookie("user_id")
    await AuthService.logout(request.cookies.get("booking_refresh_token"))
    return {"message": "Logged out successfully"}


@router_auth.post("/refresh")
async def refresh_token(
    request: Request,
    response: Response
) -> SToken:
    if (brt := request.cookies.get("booking_refresh_token", None)) != None:

        new_token = await AuthService.refresh_token(
            uuid.UUID(brt)
        )
    else:
        raise InvalidTokenException
    response.set_cookie(
        'booking_access_token',
        new_token.access_token,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=True,
    )
    response.set_cookie(
        'booking_refresh_token',
        new_token.refresh_token,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 30 * 24 * 60,
        httponly=True,
    )
    return new_token


@router_users.get("/me")
async def read_users_me(current_user: Users = Depends(get_current_user)) -> SUser:
    return TypeAdapter(SUser).validate_python(current_user).model_dump()


@router_users.get("/all_users")
async def read_users_all(
    current_user: Users = Depends(get_current_admin_user)
) -> List[SUser]:
    res = await UsersDAO.find_all()
    res = [TypeAdapter(SUser).validate_python(user).model_dump() for user in res]
    return res


@router_users.get("/verify/{user_id}")
async def verify_new_user(user_id: uuid.UUID):
    res = await UsersDAO.update(
        Users.id == user_id,
        data=SUserVerify(is_verified=True))
    if res:
        return 'Ваша регистрация подтверждена'
    else:
        return 'Ошибка'
    
@router_users.post("/update_personal_data")
async def update_personal_data(
    user_data: SUserUpdate,
    user: Users = Depends(get_current_user),
):
    user_update = await UsersDAO.update(
        Users.id == user.id,
        data=user_data) 
    


@router_auth.post("/change_pass")
async def change_password(
    user_data: SUserReAuth,
    current_user: Users = Depends(get_current_user)
):
    user = await AuthService.authenticate_user(current_user.email, user_data.password)
    if not user:
        raise IncorrectCurrentPasswordException
    if user_data.new_password != user_data.new_pass_re:
        raise PasswordNotConfirm
    user_update = await UsersDAO.update(Users.id==current_user.id,
                                data={"hashed_password": get_password_hash(user_data.new_password)})
    if user_update:
        return {"message": "Пароль сменен"}
    return {"message": "Ошибка"}



