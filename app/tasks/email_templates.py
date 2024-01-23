from email.message import EmailMessage
from app.config import settings
from pydantic import EmailStr


def create_booking_confirmation_templates(
        booking: dict,
        email_to: EmailStr,
):
    email = EmailMessage()

    email["Subject"] = "Подтверждение бронирования"
    email["From"] = settings.SMTP_USER
    email["To"] = email_to

    email.set_content(
        f"""
        <h1>Подтвердите бронирование</h1>
        Вы забронировали отель с {booking["date_from"]} по {booking["date_to"]}
        """,
        subtype="html"
    )

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
        """,
        subtype="html"
    )

    return email
