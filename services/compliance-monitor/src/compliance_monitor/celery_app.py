"""Celery application configuration for Compliance Monitor."""

from celery import Celery
from celery.schedules import crontab

from compliance_monitor.config import settings

celery_app = Celery(
    "compliance_monitor",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=[
        "compliance_monitor.tasks.schema_check",
        "compliance_monitor.tasks.quality_check",
        "compliance_monitor.tasks.availability_check",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes max per task
    task_soft_time_limit=240,  # Soft limit at 4 minutes
    worker_prefetch_multiplier=1,  # One task at a time per worker
    task_acks_late=True,  # Acknowledge after task completes
)

# Scheduled tasks using Celery Beat
celery_app.conf.beat_schedule = {
    "check-all-schemas": {
        "task": "compliance_monitor.tasks.schema_check.check_all_schemas",
        "schedule": crontab(minute="*/5"),  # Every 5 minutes
        "options": {"queue": "compliance"},
    },
    "check-all-quality": {
        "task": "compliance_monitor.tasks.quality_check.check_all_quality",
        "schedule": crontab(minute="*/15"),  # Every 15 minutes
        "options": {"queue": "compliance"},
    },
    "check-all-availability": {
        "task": "compliance_monitor.tasks.availability_check.check_all_availability",
        "schedule": crontab(minute="*"),  # Every minute
        "options": {"queue": "compliance"},
    },
}

# Task routing
celery_app.conf.task_routes = {
    "compliance_monitor.tasks.*": {"queue": "compliance"},
}
