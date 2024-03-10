import celery
from app.cart.dao import CartDao
from app.tasks.celery import celery
from app.bookings.dao import BookingDAO
from app.tasks.email_templates import create_booking_notice_template
from app.config import settings
from app.loger import logger
import smtplib
import asyncio

from app.users.service import AuthService

async def notice(days: int): 
    bookings = await BookingDAO.find_all_nearest_bookings(days)

    msgs = []
    if bookings:
        logger.debug(f"{bookings=}")
        for booking in bookings:
            booking_data = {
                "date_to": booking.date_to,
                "date_from": booking.date_from,
                "room_name": booking.room.name,
                "img": booking.room.image_id,
            }
            email_to = settings.SMTP_USER
            msg_content = create_booking_notice_template(booking_data, email_to, days)
            msgs.append(msg_content)

        with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.login(settings.SMTP_USER, settings.SMTP_PASS)
            for msg_content in msgs:
                server.send_message(msg_content)
        logger.info("Successfully sent reminding messages")

async def del_old_tokens():
    logger.debug("delete_tokens=")
    res = await AuthService.delete_old_refresh_token()
    logger.info("Successfully delete old tokens")

async def del_book_from_cart(days):
    logger.debug("delete_old_book=")
    res = await CartDao.delete_old_book_from_cart(days)
    logger.info("Successfully delete from cart")


@celery.task(name="notice_one_day")
def periodic_task_1():
    asyncio.run(notice(1))


@celery.task(name="notice_three_days")
def periodic_task_2():
    asyncio.run(notice(3))


@celery.task(name="delete_old_token")
def periodic_task_3():
    asyncio.run(del_old_tokens())


@celery.task(name="delete_old_book_from_cart")
def periodic_task_4():
    asyncio.run(del_book_from_cart(180))
    



