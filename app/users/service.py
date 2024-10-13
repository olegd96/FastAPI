import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import HTTPException, status
from jose import jwt
from sqlalchemy import extract, func

from app.users.utils import verify_password
from app.users.schemas import SRefreshSessionUpdate, SToken, SRefreshSessionCreate
from app.users.models import RefreshSessionModel, Users
from app.users.dao import UsersDAO, RefreshSessionDAO
from app.config import settings
from app.exceptions import InvalidTokenException, TokenExpiredException


class AuthService:
    @classmethod
    async def create_token(cls, user_id: uuid.UUID) -> SToken:
        access_token = cls._create_access_token(user_id)
        refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        refresh_token = cls._create_refresh_token()

        await RefreshSessionDAO.add(
            **SRefreshSessionCreate(
                user_id=user_id,
                refresh_token=refresh_token,
                expires_in=refresh_token_expires.total_seconds(),
            ).model_dump()
        )
        return SToken(
            access_token=access_token, refresh_token=refresh_token, token_type="bearer"
        )

    @classmethod
    async def refresh_token(cls, token: uuid.UUID) -> SToken:
        refresh_session = await RefreshSessionDAO.find_one_or_none(refresh_token=token)
        if refresh_session is None:
            raise InvalidTokenException
        if datetime.now(timezone.utc) >= refresh_session.created_at + timedelta(
            seconds=refresh_session.expires_in
        ):
            await RefreshSessionDAO.delete(id=refresh_session.id)
            raise TokenExpiredException

        user = await UsersDAO.find_one_or_none(id=refresh_session.user_id)
        if user is None:
            raise InvalidTokenException

        access_token = cls._create_access_token(user.id)
        refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        refresh_token = cls._create_refresh_token()

        await RefreshSessionDAO.update(
            RefreshSessionModel.id == refresh_session.id,
            data=SRefreshSessionUpdate(
                refresh_token=refresh_token,
                expires_in=refresh_token_expires.total_seconds(),
            ),
        )
        return SToken(
            access_token=access_token, refresh_token=refresh_token, token_type="bearer"
        )

    @classmethod
    async def authenticate_user(cls, email: str, password: str) -> Optional[Users]:
        user = await UsersDAO.find_one_or_none(email=email)
        if user and verify_password(password, user.hashed_password):
            return user
        return None

    @classmethod
    async def logout(cls, token: uuid.UUID) -> None:
        refresh_session = await RefreshSessionDAO.find_one_or_none(refresh_token=token)
        if refresh_session:
            await RefreshSessionDAO.delete(id=refresh_session.id)

    @classmethod
    def _create_access_token(cls, user_id: uuid.UUID) -> str:
        to_encode = {
            "sub": str(user_id),
            "exp": datetime.now(timezone.utc)
            + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        }
        encoded_jwt = jwt.encode(
            to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
        )
        return f"Bearer {encoded_jwt}"

    @classmethod
    def _create_refresh_token(cls) -> uuid.UUID:
        return uuid.uuid4()

    @classmethod
    async def delete_old_refresh_token(cls):
        res = await RefreshSessionDAO.delete_old()
