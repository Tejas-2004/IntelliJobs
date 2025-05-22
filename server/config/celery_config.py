from celery import Celery, Task
from flask import Flask
import os
from dotenv import load_dotenv
import eventlet

eventlet.monkey_patch()

load_dotenv()

# Initialize Celery
celery_app = Celery('intellijobs',
                    broker=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
                    backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0'))

# Celery Beat Schedule
celery_app.conf.beat_schedule = {
    'scrape-and-update-vectors': {
        'task': 'server.tasks.tasks.scrape_and_update_vectors',
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
    include=['tasks.tasks']  # Changed from server.tasks.tasks to match your import structure
)

# Add the function for Flask integration
def celery_init_app(app: Flask) -> Celery:
    class FlaskTask(Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    # Create a new Celery app with Flask integration
    flask_celery = Celery(app.name, task_cls=FlaskTask)
    flask_celery.config_from_object(app.config["CELERY"])
    
    # Copy configuration from the existing celery_app
    flask_celery.conf.update(celery_app.conf)
    
    flask_celery.set_default()
    app.extensions["celery"] = flask_celery
    return flask_celery
