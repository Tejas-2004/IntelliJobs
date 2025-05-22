import eventlet
eventlet.monkey_patch()

from config.celery_config import celery_app

# This file is used just to run the Celery worker
