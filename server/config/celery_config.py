from celery import Celery
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize Celery
celery_app = Celery('intellijobs',
                    broker=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
                    backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0'))

# Celery Beat Schedule
celery_app.conf.beat_schedule = {
    'scrape-and-update-vectors': {
        'task': 'server.tasks.scrape_and_update_vectors',
        'schedule': 86400.0,  # Run every 24 hours
    },
}

# Optional configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
) 