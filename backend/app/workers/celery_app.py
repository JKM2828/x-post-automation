from celery import Celery
from celery.schedules import crontab
from app.config import settings

# Create Celery app
celery_app = Celery(
    "xpost_automation",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=['app.workers.tasks']
)

# Configure Celery
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
)

# Configure periodic tasks
celery_app.conf.beat_schedule = {
    'post-scheduled-tweets': {
        'task': 'app.workers.tasks.post_scheduled_tweets',
        'schedule': crontab(minute='*/5'),  # Every 5 minutes
    },
    'fetch-tweet-metrics': {
        'task': 'app.workers.tasks.fetch_tweet_metrics',
        'schedule': crontab(minute='*/15'),  # Every 15 minutes
    },
    'retrain-viral-model': {
        'task': 'app.workers.tasks.retrain_viral_model',
        'schedule': crontab(hour=0, minute=0),  # Daily at midnight
    },
}
