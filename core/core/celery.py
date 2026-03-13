import os
from celery import Celery

# Point Celery at your Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('rfp_system')

# Load config from Django settings, looking for CELERY_ prefix
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks.py files in all installed apps
app.autodiscover_tasks()