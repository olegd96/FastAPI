# from datetime import datetime, timedelta
# import uuid
# from passlib.context import CryptContext
# from jose import jwt
# from pydantic import EmailStr

# from app.config import settings
# from app.users.dao import UsersDAO


# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# def get_password_hash(password: str) -> str:
#     return pwd_context.hash(password)


# def verify_password(plain_password, hashed_password) -> bool:
#     return pwd_context.verify(plain_password, hashed_password)


# def create_access_token(data: dict) -> str:
#     to_encode = data.copy()
#     expire = (datetime.utcnow() + timedelta(settings.ACCESS_TOKEN_EXPIRE_MINUTES)).timestamp()
#     to_encode.update({"exp": expire})
#     encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, settings.ALGORITHM)
#     return f"Bearer {encoded_jwt}"

# def create_refresh_token():
#     return uuid.uuid4()


# async def authenticate_user(email: EmailStr, password: str):
#     user = await UsersDAO.find_one_or_none(email=email)
#     if user and verify_password(password, user.hashed_password):  
#         return user
#     return None
