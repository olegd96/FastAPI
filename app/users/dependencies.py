from datetime import datetime
from typing import Optional
import uuid
from fastapi import Depends, HTTPException, Request, status
from jose import jwt, JWTError
from pydantic import TypeAdapter

from app.config import settings
from app.exceptions import IncorrectTokenFormatException, TokenAbsentException, TokenExpiredException, UserIsNotPresentException
from app.users.dao import UsersDAO
from app.users.models import Users
from app.users.schemas import SUser
from app.users.utils import OAuth2PasswordBearerWithCookie

oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="/auth/login")


def get_token(request: Request):
    token = request.cookies.get("booking_access_token")
    if not token:
        raise TokenAbsentException
    return token


async def get_current_user(token: str = Depends(oauth2_scheme)) -> Optional[Users]:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
    except JWTError:
        raise IncorrectTokenFormatException
    expire: str = payload.get("exp")
    if (not expire) or (int(expire) < datetime.utcnow().timestamp()):
        raise TokenExpiredException  
    user_id: str = payload.get("sub")
    if not user_id:
        raise UserIsNotPresentException
    user = await UsersDAO.find_one_or_none(id=uuid.UUID(user_id))
    if not user:
        raise UserIsNotPresentException 
    return user

async def get_current_active_user(current_user: Users = Depends(get_current_user)) -> Users:
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User is not active")
    return current_user


async def get_current_admin_user(current_user: Users = Depends(get_current_user)):
    #if current_user.role != "admin":
        #raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return current_user

