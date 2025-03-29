"""Celery task for monitoring macroeconomic indicators.

This module contains the Celery task that periodically checks for significant
changes in macroeconomic indicators like CPI (Consumer Price Index).
"""

from app.services.beat_scheduler import celery_app  # Import the existing Celery instance
from app.services.notifications import process_macro_alert

@celery_app.task
def check_cpi_spike() -> str:
    """Periodic task to check for CPI spikes and trigger alerts.

    This Celery task executes the macroeconomic alert processing function
    and handles any potential errors that may occur during execution.

    Returns:
        str: A result message indicating either:
            - The output from process_macro_alert() on success
            - "Error" if an exception occurred

    Note:
        Errors are printed to stdout in addition to being returned as a string.
        This task is typically scheduled to run at regular intervals.
    """
    try:
        result = process_macro_alert()
        return result
    except Exception as e:
        print(f"Error in check_cpi_spike: {e}")
        return "Error"