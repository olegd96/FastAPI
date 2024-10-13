import asyncio
import time
import uuid
from asyncio import sleep
from contextlib import asynccontextmanager

import sentry_sdk
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
from fastapi_versioning import VersionedFastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from pydantic import BaseModel
from redis import asyncio as aioredis
from sqladmin import Admin, ModelView

from app.admin.auth import authentication_backend
from app.admin.views import (
    BookingsAdmin,
    CartAdmin,
    FavourAdmin,
    HotelsAdmin,
    RoomsAdmin,
    UsersAdmin,
)

from app.bookings.router import router as router_bookings
from app.cart.router import router as router_cart
from app.config import settings
from app.database import engine
from app.exceptions import RequestAttorneyException
from app.favourites.router import router as router_fav
from app.hotels.rooms import router
from app.hotels.router import router as router_hotels
from app.images.router import router as router_images
from app.importer.router import router as router_importer
from app.loger import logger
from app.pages.router import router as router_pages
from app.prometheus.router import router as prometheus_router
from app.users.models import Users
from app.users.router import router_auth, router_users
from app.web_socket.router import router as router_chat
from app.S3.router import router as router_s3
from app.loger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis = aioredis.from_url(f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}")
    FastAPICache.init(RedisBackend(redis), prefix="cache")
    logger.info(msg="start_app")
    yield
    logger.info(msg="shutdown_app")


app = FastAPI(lifespan=lifespan)


@app.exception_handler(RequestAttorneyException)
async def attorney_exception_handler(request: Request, exc: RequestAttorneyException):
    return RedirectResponse("/pages")


app.include_router(router_auth)
app.include_router(router_users)
app.include_router(router_bookings)
app.include_router(router_hotels)
app.include_router(router_images)
app.include_router(router_pages)
app.include_router(router_importer)
app.include_router(prometheus_router)
app.include_router(router_cart)
app.include_router(router_fav)
app.include_router(router_chat)
app.include_router(router_s3)


sentry_sdk.init(
    dsn="https://5c7f688a239ae54b0a58d59f1d3ecb49@o4506548030865408.ingest.sentry.io/4506548074905600",
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
)

origins = [
    # 3000 - порт, на котором работает фронтенд на React.js
    "http://localhost:3000",
    "http://localhost",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
    allow_headers=[
        "Content-Type",
        "Set-Cookie",
        "Access-Control-Allow-Headers",
        "Access-Control-Allow-Origin",
        "Authorization",
    ],
)

""" app = VersionedFastAPI(app,
    version_format='{major}',
    prefix_format='/v{major}',
    #description='Greet users with a nice message',
    #middleware=[
    #    Middleware(SessionMiddleware, secret_key='mysecretkey')
    #]
) """

instrumentator = Instrumentator(
    should_group_status_codes=False,
    excluded_handlers=[".*admin.*", "/metrics"],
)

instrumentator.instrument(app).expose(app)

app.mount("/static", StaticFiles(directory="app/static"), "static")

admin = Admin(app, engine, authentication_backend=authentication_backend)
admin.add_view(UsersAdmin)
admin.add_view(BookingsAdmin)
admin.add_view(HotelsAdmin)
admin.add_view(RoomsAdmin)
admin.add_view(CartAdmin)
admin.add_view(FavourAdmin)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(
        "Request execution time", extra={"process_time": round(process_time, 4)}
    )
    response.headers["X-Process-Time"] = str(process_time)
    return response
