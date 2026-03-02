<<<<<<< HEAD
from celery import Celery
from app.core.config import settings

celery = Celery(
    "coreops",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)
=======
from celery import Celery
from app.core.config import settings

celery = Celery(
    "coreops",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)
>>>>>>> 21599b0b39eba37876fc43d9838497fbe2974000
celery.conf.task_track_started = True