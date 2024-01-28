from celery import Celery

from app.config import settings
from celery import schedules

celery = Celery(
    "tasks",
    broker=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
    broker_connection_retry_on_startup = True,
    include=["app.tasks.tasks",
             "app.tasks.scheduled",
             ]
)

celery.conf.beat_schedule = {
    "app_periodic_tasks": {
        "task": "notice_one_day",
        #"schedule": 60,
        "schedule": schedules.crontab(minute="30", hour="15"),
    }
}
