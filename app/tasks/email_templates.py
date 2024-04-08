from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText  # Added
from email.mime.image import MIMEImage
from email.message import EmailMessage
import uuid
from app.config import settings
from pydantic import EmailStr

from app.users.models import Users

attachment = 'app/static/images/simple-booking.jpg'


def create_booking_confirmation_templates(
        booking: dict,
        email_to: EmailStr,
):
    email = MIMEMultipart()

    email["Subject"] = "Подтверждение бронирования"
    email["From"] = settings.SMTP_USER
    email["To"] = email_to
    
    body = f"""
        <h1>Подтвердите бронирование</h1>
        Вы забронировали отель с {booking["date_from"]} по {booking["date_to"]}
        """
    msgText = MIMEText('<b>%s</b><br/><img src="cid:%s"/><br/>' % (body, attachment), 'html')
    email.attach(msgText)
    email.add_header('Content-Disposition', 'attachment', filename='app/static/images/simple-booking.jpg')
    with open(attachment, "rb") as file:
        image = MIMEImage(file.read())
    
    image.add_header('Content-ID', '<{}>'.format(attachment))
    email.attach(image)


    return email

def create_booking_notice_template(
        booking: dict,
        email_to: EmailStr,
        days: int,


):
    alph = {
        1: "день",
        3: "дня"
    }

    email = EmailMessage()

    email["Subject"] = f"Остался {days} {alph[days]} до заселения"
    email["From"] = settings.SMTP_USER
    email["To"] = email_to

    email.set_content(
        f"""
        <h1>Напоминание о бронировании</h1>
        Вы забронировали отель с {booking["date_from"]} по {booking["date_to"]}
        <h2>{booking["room_name"]}</h2>
         <img src='/static/images/resized_200_100_'{booking['img']}'.webp'
                    onerror="this.src='static/images/simple-booking.jpg';">
        """,
        subtype="html"
    )

    return email


def create_registration_confirmation_templates(
        user_id: uuid.UUID,
        email_to: EmailStr,
):
    email = MIMEMultipart()

    email["Subject"] = "Подтверждение регистрации"
    email["From"] = settings.SMTP_USER
    email["To"] = email_to
    
    body = f"""
        <h1>Подтвердите регистрацию</h1>
        Вы зарегистрировались на ONBOOK,
        пожалуйста, подтвердите регистрацию,
        для этого перейдите по
        <a href="http://94.241.143.220/auth/verify/{user_id}" style="color: blue;">ссылкe</a>.
        Если это были не вы, не отвечайте на данное сообщение.
        """
    msgText = MIMEText('<b>%s</b><br/><img src="cid:%s"/><br/>' % (body, attachment), 'html')
    email.attach(msgText)
    email.add_header('Content-Disposition', 'attachment', filename='app/static/images/simple-booking.jpg')
    with open(attachment, "rb") as file:
        image = MIMEImage(file.read())
    
    image.add_header('Content-ID', '<{}>'.format(attachment))
    email.attach(image)


    return email
