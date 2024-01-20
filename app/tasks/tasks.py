import codecs
import os
import shutil
from typing import Literal
from fastapi import Depends
from pydantic import EmailStr, TypeAdapter
from sqlalchemy import insert
from app.bookings.models import Bookings
from app.hotels.models import Hotels
from app.hotels.rooms.models import Rooms
from app.tasks.celery import celery
from PIL import Image
from pathlib import Path
from app.config import settings
from app.database import async_session_taskmaker
from sqlalchemy.exc import SQLAlchemyError
from app.tasks.email_templates import create_booking_confirmation_templates
import smtplib
import csv
from app.dao.base import BaseDAO
from app.users.dependencies import get_current_user
from app.users.models import Users
from app.loger import logger
from app.importer.utils import convert_csv_to_postgres_format


@celery.task
def process_pic(
    path: str,
):
    im_path = Path(path)
    im = Image.open(im_path)
    im_resized_500_300 = im.resize((500, 300))
    im_resized_200_100 = im.resize((200, 200))
    im_resized_500_300.save(f"app/static/images/resized_500_300_{im_path.name}")
    im_resized_200_100.save(f"app/static/images/resized_200_100_{im_path.name}")


@celery.task
def send_booking_confirmation_email(
    booking: dict,
    email_to: EmailStr,
):
    email_to = settings.SMTP_USER
    msg_content = create_booking_confirmation_templates(booking, email_to)
    with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.login(settings.SMTP_USER, settings.SMTP_PASS)
        server.send_message(msg_content)

@celery.task
async def process_table_data(
    table_name: Literal['hotels', 'bookings', 'rooms'],
    file_path: str,
    user: Users = Depends(get_current_user)
):
    table_data = None
    table = {
        "hotels": Hotels,
        "rooms": Rooms,
        "bookings": Bookings
    }
    try:
        
        with open(file_path, "r", encoding="UTF-8") as file:
            table_data = csv.DictReader(file, delimiter=";")
            table_data = convert_csv_to_postgres_format(table_data)
            async with async_session_taskmaker() as session:
                query = insert(table[table_name])
                await session.execute(query, table_data)
                await session.commit()
        os.remove(file_path)
    except (SQLAlchemyError, Exception) as e:
        if isinstance(e, SQLAlchemyError):
            msg = "Database Exc"
        elif isinstance(e, Exception):
            msg = "Unknown exc"
        msg += ": Cannot add table"
        extra = {
            "user_id": user,
            "table": table_name,
            "file": file_path,         
        }
        logger.error(msg, extra=extra, exc_info=True)

    