import celery
from app.tasks.celery import celery
from app.bookings.dao import BookingDAO
from app.tasks.email_templates import create_booking_notice_template
from app.config import settings
import smtplib
import asyncio

async def notice(days: int): 
    bookings_list = await BookingDAO.find_all_nearest_bookings(days)
    for booking in bookings_list:
        email_to = settings.SMTP_USER
        msg_content = create_booking_notice_template(booking, email_to, days)
        with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.login(settings.SMTP_USER, settings.SMTP_PASS)
            server.send_message(msg_content)

@celery.task(name="notice_one_day")
def periodic_task_1():
    asyncio.run(notice(1))
    



@celery.task(name="notice_three_day")
def periodic_task_2():
    asyncio.run(notice(3))