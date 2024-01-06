from celery import Celery

celery = Celery(
    "tasks",
    broker = "redis://localhost:6379",
    broker_connection_retry_on_startup = True,
    include=["app.tasks.tasks"]
)