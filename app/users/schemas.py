from turtle import st
from typing import List, Optional
import uuid
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class SUserAuth(BaseModel):
    email: EmailStr
    password: str

class SUserBase(BaseModel):
    email: Optional[EmailStr] = Field(None)
    fio: Optional[str] = Field("")
    telephone: Optional[str] = Field("")
    is_active: bool = Field(True)
    is_verified: bool = Field(False)
    is_administrator: bool = Field(False)

class SUserReg(SUserBase):
    email: EmailStr
    password: str

class SUserDB(SUserBase):
    hashed_password: Optional[str] = None

class SUser(SUserBase):
    id: uuid.UUID
    email: EmailStr
    fio: str|None
    telephone: str|None
    is_active: bool
    is_verified: bool
    is_administrator: bool

    model_config=ConfigDict(from_attributes=True)


class SUserInfo(SUser):
    bookings: List["Bookings"]
    carts: List["Carts"]
    favourites: List["Favourites"]

    model_config=ConfigDict(from_attributes=True)

class SRefreshSessionCreate(BaseModel):
    user_id: uuid.UUID
    refresh_token: uuid.UUID
    expires_in: int

class SRefreshSessionUpdate(SRefreshSessionCreate):
    user_id: Optional[uuid.UUID] = Field(None)

class SToken(BaseModel):
    access_token: str
    refresh_token: uuid.UUID
    token_type: str

