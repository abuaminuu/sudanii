import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# load root dir name
app = Celery("config")

# Load configuration from Django settings, using 'CELERY_' prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover task modules from all registered INSTALLED_APPS (e.g., orders/tasks.py)
app.autodiscover_tasks()
