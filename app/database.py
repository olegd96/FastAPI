from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from motor import motor_asyncio

from app.config import settings
import grpc

from app.weather_pb2_grpc import WeatherGrpcServiceStub

if settings.MODE == "TEST":
    DATABASE_URL = settings.TEST_DATABASE_URL
    DATABASE_PARAMS = {"poolclass": NullPool}
else:
    DATABASE_PARAMS = {}
    DATABASE_URL = settings.DATABASE_URL

engine = create_async_engine(DATABASE_URL, pool_pre_ping=True, **DATABASE_PARAMS)
engine_nullpool = create_async_engine(DATABASE_URL, **{"poolclass": NullPool})
async_session_maker = async_sessionmaker(bind=engine, expire_on_commit=False)
async_session_taskmaker = async_sessionmaker(
    bind=engine_nullpool, expire_on_commit=False
)
client: motor_asyncio.AsyncIOMotorClient = motor_asyncio.AsyncIOMotorClient(
    settings.MONGO_URL, connect=True
)
database_mongo = client[settings.MONGO_NAME]
channel = grpc.aio.insecure_channel("localhost:50051")
grpc_client = WeatherGrpcServiceStub(channel)


class Base(DeclarativeBase):
    pass
