from celery import Celery
from app.core.config import settings

celery = Celery(
    "coreops",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.worker.tasks"],
)

celery.conf.timezone = "UTC"

celery.conf.beat_schedule = {
    "coreops-tick-every-10-seconds": {
        "task": "coreops.tick",
        "schedule": 10.0,
    },
}