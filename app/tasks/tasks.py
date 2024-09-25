import aiobotocore
import uuid
import asyncio
from pydantic import EmailStr
from sqlalchemy import insert
from app.bookings.dao import BookingDAO
from app.tasks.celery import celery
from PIL import Image
from pathlib import Path
from app.config import settings
from app.loger import logger
from app.S3.s3client import s3_client
import os

from app.tasks.email_templates import create_booking_confirmation_templates, create_booking_notice_template, create_registration_confirmation_templates
import smtplib


async def s3_1(path: str):
        await s3_client.upload_file(f"/static/images/resized_500_300_{path}")

async def s3_2(path: str):
    await s3_client.upload_file(f"/static/images/resized_200_100_{path}")

async def s3_download(im_path: str):
     await s3_client.download_file(im_path)
     

async def main(path: str):
    upload_task_500_300 = asyncio.create_task(s3_1(path))
    upload_task_200_100 = asyncio.create_task(s3_2(path))
    await asyncio.gather(upload_task_500_300, upload_task_200_100)

async def main_1(im_path: str):
     download_task = asyncio.create_task(s3_download(im_path))
     await asyncio.gather(download_task)


@celery.task(bind=True, default_retry_delay=300, max_retries=5)
def download_pic(
    *args, path: str, 
):
    obj_name = path
    asyncio.run(main_1(obj_name))


@celery.task(bind=True, default_retry_delay=300, max_retries=5)
def process_pic(
    *args, path: str, 
):
    obj_name = path
    im = Image.open(f"/static/images/{obj_name}")
    im_resized_500_300 = im.resize((500, 300))
    im_resized_200_100 = im.resize((200, 200))
    im_resized_500_300.save(f"/static/images/resized_500_300_{obj_name}")
    im_resized_200_100.save(f"/static/images/resized_200_100_{obj_name}")
    asyncio.run(main(obj_name))
    os.remove(f"/static/images/resized_500_300_{obj_name}")
    os.remove(f"/static/images/resized_200_100_{obj_name}")


@celery.task
def send_booking_confirmation_email(
    *args, 
    booking: dict,
    email_to: EmailStr,
):
    msg_content = create_booking_confirmation_templates(booking, email_to)
    with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.login(settings.SMTP_USER, settings.SMTP_PASS)
        server.send_message(msg_content) 

@celery.task(bind=True, default_retry_delay=300, max_retries=5)
def send_registration_confirmation_email(
    *args, 
    user_id: uuid.UUID,
    email_to: EmailStr,
):
    msg_content = create_registration_confirmation_templates(user_id, email_to)
    with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.login(settings.SMTP_USER, settings.SMTP_PASS)
        server.send_message(msg_content) 

  