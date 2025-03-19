import os
import logging
from celery import Celery
from celery.schedules import crontab
from dotenv import load_dotenv

load_dotenv()  # Load environment variables

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")  # Default fallback

celery_app = Celery(
    "tasks",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["app.services.celery_worker"]
)

celery_app.conf.beat_schedule = {
    "check-cpi-every-10-minutes": {
        "task": "app.services.celery_worker.check_cpi_spike",  # Fully-qualified task name
        "schedule": 600.0,  # Every 10 minutes
    },
}
celery_app.conf.timezone = "UTC"

logger = logging.getLogger(__name__)
