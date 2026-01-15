"""Celery Beat schedule configuration for periodic tasks."""
from celery.schedules import crontab

# Celery Beat Schedule
# This configuration defines when periodic tasks should run
CELERYBEAT_SCHEDULE = {
    # Ingest all RSS feeds every 2 hours
    'ingest-all-feeds': {
        'task': 'app.tasks.ingestion_tasks.ingest_all_feeds',
        'schedule': crontab(minute=0, hour='*/2'),  # Every 2 hours on the hour
        'options': {
            'expires': 3600,  # Task expires after 1 hour if not picked up
        }
    },

    # Ingest all YouTube channels every 4 hours
    'ingest-all-youtube-channels': {
        'task': 'app.tasks.ingestion_tasks.ingest_all_youtube_channels',
        'schedule': crontab(minute=30, hour='*/4'),  # Every 4 hours at :30
        'options': {
            'expires': 3600,
        }
    },

    # Comprehensive ingestion from all sources once daily
    'ingest-all-sources-daily': {
        'task': 'app.tasks.ingestion_tasks.ingest_all_sources',
        'schedule': crontab(hour=3, minute=0),  # Daily at 3:00 AM
        'options': {
            'expires': 7200,  # Expires after 2 hours
        }
    },

    # Clean up old processed queue items weekly
    'cleanup-old-queue-items': {
        'task': 'app.tasks.ingestion_tasks.cleanup_old_queue_items',
        'schedule': crontab(day_of_week=0, hour=2, minute=0),  # Sundays at 2:00 AM
        'kwargs': {'days': 30},  # Keep items for 30 days
        'options': {
            'expires': 3600,
        }
    },
}

# Alternative schedule examples (commented out):

# More frequent RSS ingestion for breaking news (every 30 minutes)
# 'frequent-rss-ingestion': {
#     'task': 'app.tasks.ingestion_tasks.ingest_all_feeds',
#     'schedule': crontab(minute='*/30'),
# },

# YouTube ingestion during business hours only
# 'business-hours-youtube': {
#     'task': 'app.tasks.ingestion_tasks.ingest_all_youtube_channels',
#     'schedule': crontab(hour='9-17', minute=0),  # Every hour from 9 AM to 5 PM
# },

# Cleanup more frequently (daily instead of weekly)
# 'daily-cleanup': {
#     'task': 'app.tasks.ingestion_tasks.cleanup_old_queue_items',
#     'schedule': crontab(hour=1, minute=0),  # Daily at 1:00 AM
#     'kwargs': {'days': 30},
# },
