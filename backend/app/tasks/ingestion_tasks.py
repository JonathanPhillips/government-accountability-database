"""Celery tasks for automated ingestion."""
from typing import List, Dict
from app.celery_app import celery_app
from app.database import SessionLocal
from app.services.rss_ingester import RSSIngester
from app.models.base import SourceTypeEnum
import logging

logger = logging.getLogger(__name__)

# RSS Feed Sources - Government Accountability Focused
RSS_FEED_SOURCES = [
    # Investigative Journalism
    {
        "url": "https://www.propublica.org/feeds/propublica/main",
        "source_type": SourceTypeEnum.NEWS_PRIMARY,
        "max_entries": 10
    },
    {
        "url": "https://theintercept.com/feed/",
        "source_type": SourceTypeEnum.NEWS_PRIMARY,
        "max_entries": 10
    },
    {
        "url": "http://feeds.bbci.co.uk/news/rss.xml",
        "source_type": SourceTypeEnum.NEWS_PRIMARY,
        "max_entries": 10
    },
    # Civil Liberties & Digital Rights
    {
        "url": "https://www.eff.org/rss/updates.xml",
        "source_type": SourceTypeEnum.NGO_REPORT,
        "max_entries": 10
    },
    # Backup news sources
    {
        "url": "https://feeds.npr.org/1001/rss.xml",
        "source_type": SourceTypeEnum.NEWS_PRIMARY,
        "max_entries": 5
    },
]


@celery_app.task(bind=True, max_retries=3)
def ingest_rss_feed(self, feed_url: str, source_type: str, max_entries: int = 10) -> Dict:
    """
    Ingest a single RSS feed.

    Args:
        feed_url: URL of the RSS feed
        source_type: Type of source (news_primary, ngo_report, etc.)
        max_entries: Maximum number of entries to process

    Returns:
        Dictionary with ingestion results
    """
    db = SessionLocal()
    try:
        logger.info(f"Starting RSS feed ingestion: {feed_url}")

        # Convert string to enum
        source_type_enum = SourceTypeEnum(source_type)

        # Ingest feed
        queue_items = RSSIngester.ingest_feed(
            db=db,
            feed_url=feed_url,
            source_type=source_type_enum,
            max_entries=max_entries
        )

        result = {
            "feed_url": feed_url,
            "entries_added": len(queue_items),
            "status": "success"
        }

        logger.info(f"Successfully ingested {len(queue_items)} entries from {feed_url}")
        return result

    except Exception as e:
        logger.error(f"Error ingesting feed {feed_url}: {str(e)}")

        # Retry with exponential backoff
        try:
            raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))
        except self.MaxRetriesExceededError:
            return {
                "feed_url": feed_url,
                "entries_added": 0,
                "status": "failed",
                "error": str(e)
            }
    finally:
        db.close()


@celery_app.task
def ingest_all_feeds() -> List[Dict]:
    """
    Ingest all configured RSS feeds.

    This task is scheduled to run periodically via Celery Beat.

    Returns:
        List of ingestion results for each feed
    """
    logger.info(f"Starting scheduled ingestion of {len(RSS_FEED_SOURCES)} feeds")

    results = []
    for feed in RSS_FEED_SOURCES:
        try:
            # Trigger individual feed ingestion task
            result = ingest_rss_feed.delay(
                feed_url=feed["url"],
                source_type=feed["source_type"].value,
                max_entries=feed.get("max_entries", 10)
            )

            results.append({
                "feed_url": feed["url"],
                "task_id": result.id,
                "status": "queued"
            })
        except Exception as e:
            logger.error(f"Error queueing feed {feed['url']}: {str(e)}")
            results.append({
                "feed_url": feed["url"],
                "status": "error",
                "error": str(e)
            })

    logger.info(f"Queued {len(results)} feed ingestion tasks")
    return results


@celery_app.task
def cleanup_old_queue_items(days: int = 30) -> Dict:
    """
    Clean up old ingestion queue items that have been processed or rejected.

    Args:
        days: Number of days to keep processed/rejected items

    Returns:
        Dictionary with cleanup results
    """
    from datetime import datetime, timedelta
    from app.models import IngestionQueue
    from app.models.base import IngestionStatusEnum

    db = SessionLocal()
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        # Delete old processed/rejected items
        deleted = db.query(IngestionQueue).filter(
            IngestionQueue.status.in_([
                IngestionStatusEnum.APPROVED,
                IngestionStatusEnum.REJECTED
            ]),
            IngestionQueue.updated_at < cutoff_date
        ).delete()

        db.commit()

        logger.info(f"Cleaned up {deleted} old queue items")
        return {
            "deleted_count": deleted,
            "cutoff_date": cutoff_date.isoformat(),
            "status": "success"
        }

    except Exception as e:
        db.rollback()
        logger.error(f"Error cleaning up queue items: {str(e)}")
        return {
            "deleted_count": 0,
            "status": "failed",
            "error": str(e)
        }
    finally:
        db.close()
