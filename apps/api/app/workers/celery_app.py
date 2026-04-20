from celery import Celery
from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "hero_ai",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=[
        "app.workers.script_worker",
        "app.workers.image_worker",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_max_retries=3,
)
