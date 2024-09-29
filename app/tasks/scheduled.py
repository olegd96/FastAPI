import celery
from app.cart.dao import CartDao
from app.hotels.dao import HotelsDAO
from app.hotels.models import Hotels
from app.tasks.celery import celery
from app.bookings.dao import BookingDAO
from app.tasks.email_templates import create_booking_notice_template
from app.config import settings
from app.loger import logger
import smtplib
import asyncio
import aio_pika

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
            email_to = booking.user.email
            msg_content = create_booking_notice_template(booking_data, email_to, days)
            msgs.append(msg_content)

        with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.login(settings.SMTP_USER, settings.SMTP_PASS)
            for msg_content in msgs:
                server.send_message(msg_content)
        logger.info("Successfully sent reminding messages")

async def send_cities_to_broker() -> None:
        cities = await HotelsDAO.find_all_location()
        if cities:
        # cities = ['Vladivostok', 'Moscow', 'New York', 'London', 'Berlin', 'Madrid', 'Paris', 'Oslo', 'Stockholm', 'San Francisco', 'Amsterdam', 'Novosibirsk', 'Perm', 'Oslobn', 'Marcel']
            connection: aio_pika.abc.AbstractRobustConnection = await aio_pika.connect_robust(settings.BROKER_URL)
            queue_name = 'city_queue'
            
            async with connection:
                channel = await connection.channel()
                city_exchange = await channel.declare_exchange(name="city_exchange", 
                                                        type=aio_pika.ExchangeType.DIRECT,
                                                        durable=True)
                cities_tasks = []
                while cities:
                        cities_tasks.append(asyncio.create_task(
                        city_exchange.publish(
                        aio_pika.Message(
                        body=f"{cities.pop(0)}".encode(),
                        delivery_mode=aio_pika.DeliveryMode.PERSISTENT),
                        routing_key=queue_name
                    ))
                        )
                await asyncio.gather(*cities_tasks)
                channel.close()
            await connection.close()
            logger.info("Successfully sent cities list") 

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

@celery.task(name="send_cities_to_broker")
def periodic_task_5():
    asyncio.run(send_cities_to_broker())
    



