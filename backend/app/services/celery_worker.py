# services/celery_worker.py
from celery import Celery
from app.services.notifications import process_macro_alert
from dotenv import load_dotenv
load_dotenv()  # This will load variables from .env into os.environ

celery_app = Celery(
    "tasks",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
    include=["app.services.celery_worker"]
)

@celery_app.task
def check_cpi_spike():
    result = process_macro_alert()
    return result
