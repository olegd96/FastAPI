import celery
from app.tasks.celery import celery
from app.bookings.dao import BookingDAO
from app.tasks.email_templates import create_booking_notice_template
from app.config import settings
from app.loger import logger
import smtplib
import asyncio

async def notice(days: int): 
    bookings = await BookingDAO.find_all_nearest_bookings(days)

    

    msgs = []
    if bookings:
        logger.debug(f"{bookings=}")
        for booking in bookings:
            booking_data = {
                "date_to": booking.date_to,
                "date_from": booking.date_from,
            }
            email_to = settings.SMTP_USER
            msg_content = create_booking_notice_template(booking_data, email_to, days)
            msgs.append(msg_content)

        with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.login(settings.SMTP_USER, settings.SMTP_PASS)
            for msg_content in msgs:
                server.send_message(msg_content)
        logger.info("Successfully sent reminding messages")

@celery.task(name="notice_one_day")
def periodic_task_1():
    asyncio.run(notice(1))
    



