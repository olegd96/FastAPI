from celery import Celery
from celery import schedules
from app.config import settings


celery = Celery(
    "tasks",
    broker=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
    broker_connection_retry_on_startup=True,
    include=[
        "app.tasks.tasks",
        "app.tasks.scheduled",
    ],
)

celery.conf.beat_schedule = {
    "app_periodic_tasks": {
        "task": "notice_one_day",
        # "schedule": 60,
        "schedule": schedules.crontab(minute="37", hour="19"),
    },
    "app_periodic_tasks_1": {
        "task": "notice_three_days",
        "schedule": schedules.crontab(minute="37", hour="20"),
    },
    "app_periodic_tasks_2": {
        "task": "delete_old_token",
        "schedule": schedules.crontab(minute="00", hour="23"),
    },
    "app_periodic_tasks_3": {
        "task": "delete_old_book_from_cart",
        "schedule": schedules.crontab(minute="00", hour="23", day_of_month="1"),
    },
    "app_periodic_tasks_3": {
        "task": "send_cities_to_broker",
        "schedule": schedules.crontab(minute=0, hour="*/1"),
    },
}
