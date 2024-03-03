
import uuid
from pydantic import EmailStr
from sqlalchemy import insert

from app.tasks.celery import celery
from PIL import Image
from pathlib import Path
from app.config import settings


from app.tasks.email_templates import create_booking_confirmation_templates, create_registration_confirmation_templates
import smtplib






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
def send_registration_confirmation_email(
    user_id: uuid.UUID,
    email_to: EmailStr,
):
    email_to = settings.SMTP_USER
    msg_content = create_registration_confirmation_templates(user_id, email_to)
    with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.login(settings.SMTP_USER, settings.SMTP_PASS)
        server.send_message(msg_content)    