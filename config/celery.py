import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# load root dir name
app = Celery("config")

# Load configuration from Django settings, using 'CELERY_' prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover task modules from all registered INSTALLED_APPS (e.g., orders/tasks.py)
app.autodiscover_tasks()

# celery beats config for periodic tasks
app.conf.beat_schedule = {
    "cancel_stale_unpaid_orders":{
        "task": "orders.tasks.cancel_stale_unpaid_orders",
        "schedule": crontab(minute="*/5")
    },
    "weekly_order_report": {
        "task": "orders.tasks.weekly_order_report",
        "schedule": crontab(day_of_week="monday", hour=0, minute=0)
    },
    "summary_task": {
        "task": "orders.tasks.payments_summary",
        "schedule": crontab(minute="*/1")
    }
}

