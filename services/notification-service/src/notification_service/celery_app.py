"""Celery application for Notification Service."""

from celery import Celery

from notification_service.config import settings

celery_app = Celery(
    "notification_service",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=[
        "notification_service.tasks.send_notification",
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
    task_default_queue="notifications",
    task_routes={
        "notification_service.tasks.*": {"queue": "notifications"},
    },
)
