"""Celery configuration and scheduling module.

This module sets up the Celery application instance and configures periodic tasks
for background processing. It handles the connection to Redis and scheduling of
recurring tasks.
"""

import os
import logging
from celery import Celery
from celery.schedules import crontab
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Redis connection URL with localhost as default fallback
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Initialize Celery application
celery_app = Celery(
    "tasks",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["app.services.celery_worker"]
)

# Configure periodic tasks
celery_app.conf.beat_schedule = {
    "check-cpi-every-10-minutes": {
        "task": "app.services.celery_worker.check_cpi_spike",  # Fully-qualified task name
        "schedule": 600.0,  # Every 10 minutes (in seconds)
    },
}

# Set timezone for scheduled tasks
celery_app.conf.timezone = "UTC"

# Initialize logger
logger = logging.getLogger(__name__)