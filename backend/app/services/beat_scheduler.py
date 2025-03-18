# services/beat_scheduler.py
from celery import Celery
from celery.schedules import crontab
from dotenv import load_dotenv
load_dotenv()  # This will load variables from .env into os.environ

celery_app = Celery(
    "tasks",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
    include=["app.services.celery_worker"]
)

celery_app.conf.beat_schedule = {
    "check-cpi-every-10-minutes": {
        "task": "app.services.celery_worker.check_cpi_spike",  # Fully-qualified task name
        "schedule": 600.0,  # Every 10 minutes
    },
}
celery_app.conf.timezone = "UTC"
