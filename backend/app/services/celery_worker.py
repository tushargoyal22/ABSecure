from app.services.beat_scheduler import celery_app  # Import the existing Celery instance
from app.services.notifications import process_macro_alert

@celery_app.task
def check_cpi_spike():
    try:
        result = process_macro_alert()
        return result
    except Exception as e:
        print(f"Error in check_cpi_spike: {e}")
        return "Error"
