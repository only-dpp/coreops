from celery import Celery
from app.core.config import settings

celery = Celery(
    "coreops",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)
celery.conf.task_track_started = True