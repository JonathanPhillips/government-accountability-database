"""Celery tasks for automated ingestion."""
from typing import List, Dict
from datetime import datetime
from app.celery_app import celery_app
from app.database import SessionLocal
from app.services.rss_ingester import RSSIngester
from app.services.youtube_ingester import YouTubeIngester
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

# YouTube Channel Sources - Government Accountability Focused
# YouTube provides RSS feeds for channels that can be monitored without API quota limits
YOUTUBE_CHANNEL_SOURCES = [
    # Investigative Journalism & Documentary Channels
    {
        "channel_id": "UCe02lGcO-ahAURWuxAJnjdA",  # ProPublica
        "name": "ProPublica",
        "source_type": SourceTypeEnum.VIDEO,
        "max_videos": 5
    },
    {
        "channel_id": "UCnMw7MmuZAwYGJK-r2KxLqQ",  # The Intercept
        "name": "The Intercept",
        "source_type": SourceTypeEnum.VIDEO,
        "max_videos": 5
    },
    # Civil Liberties & Digital Rights
    {
        "channel_id": "UCKPZi7rFM5oy2Ln0Z8KJQ6w",  # EFF (Electronic Frontier Foundation)
        "name": "Electronic Frontier Foundation",
        "source_type": SourceTypeEnum.VIDEO,
        "max_videos": 5
    },
    # Democracy & Accountability
    {
        "channel_id": "UCJDn07DCtlBEYe8zQNkdzzQ",  # Democracy Now!
        "name": "Democracy Now!",
        "source_type": SourceTypeEnum.VIDEO,
        "max_videos": 5
    },
    # Example of channel by username
    # {
    #     "username": "@aclu",  # ACLU
    #     "name": "ACLU",
    #     "source_type": SourceTypeEnum.VIDEO,
    #     "max_videos": 5
    # },
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


@celery_app.task(bind=True, max_retries=3)
def ingest_youtube_channel(self, channel_id: str = None, username: str = None,
                          name: str = None, source_type: str = SourceTypeEnum.VIDEO.value,
                          max_videos: int = 5) -> Dict:
    """
    Ingest videos from a YouTube channel using RSS feed.

    YouTube provides RSS feeds for channels that work without API quotas.
    Uses either channel_id or username to construct the feed URL.

    Args:
        channel_id: YouTube channel ID (e.g., UCxxxxxxxxxxxxx)
        username: YouTube channel username (alternative to channel_id)
        name: Human-readable channel name for logging
        source_type: Type of source (defaults to VIDEO)
        max_videos: Maximum number of videos to process

    Returns:
        Dictionary with ingestion results
    """
    db = SessionLocal()
    try:
        # Get feed URL
        if channel_id:
            feed_url = YouTubeIngester.get_channel_feed_url(channel_id)
            identifier = channel_id
        elif username:
            feed_url = YouTubeIngester.get_channel_feed_url_by_username(username)
            identifier = username
        else:
            raise ValueError("Either channel_id or username must be provided")

        logger.info(f"Starting YouTube channel ingestion: {name or identifier}")

        # Convert string to enum
        source_type_enum = SourceTypeEnum(source_type)

        # Ingest channel feed using RSS ingester
        queue_items = RSSIngester.ingest_feed(
            db=db,
            feed_url=feed_url,
            source_type=source_type_enum,
            max_entries=max_videos
        )

        result = {
            "channel": name or identifier,
            "feed_url": feed_url,
            "videos_added": len(queue_items),
            "status": "success"
        }

        logger.info(f"Successfully ingested {len(queue_items)} videos from {name or identifier}")
        return result

    except Exception as e:
        logger.error(f"Error ingesting YouTube channel {name or identifier}: {str(e)}")

        # Retry with exponential backoff
        try:
            raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))
        except self.MaxRetriesExceededError:
            return {
                "channel": name or (channel_id or username),
                "videos_added": 0,
                "status": "failed",
                "error": str(e)
            }
    finally:
        db.close()


@celery_app.task
def ingest_all_youtube_channels() -> List[Dict]:
    """
    Ingest all configured YouTube channels.

    This task is scheduled to run periodically via Celery Beat.

    Returns:
        List of ingestion results for each channel
    """
    logger.info(f"Starting scheduled ingestion of {len(YOUTUBE_CHANNEL_SOURCES)} YouTube channels")

    results = []
    for channel in YOUTUBE_CHANNEL_SOURCES:
        try:
            # Trigger individual channel ingestion task
            result = ingest_youtube_channel.delay(
                channel_id=channel.get("channel_id"),
                username=channel.get("username"),
                name=channel.get("name"),
                source_type=channel["source_type"].value,
                max_videos=channel.get("max_videos", 5)
            )

            results.append({
                "channel": channel.get("name", channel.get("channel_id", channel.get("username"))),
                "task_id": result.id,
                "status": "queued"
            })
        except Exception as e:
            logger.error(f"Error queueing channel {channel.get('name')}: {str(e)}")
            results.append({
                "channel": channel.get("name", "unknown"),
                "status": "error",
                "error": str(e)
            })

    logger.info(f"Queued {len(results)} YouTube channel ingestion tasks")
    return results


@celery_app.task
def ingest_all_sources() -> Dict:
    """
    Ingest from all configured sources (RSS feeds and YouTube channels).

    This is the master task that triggers both RSS and YouTube ingestion.

    Returns:
        Dictionary with ingestion results for all sources
    """
    logger.info("Starting comprehensive ingestion from all sources")

    # Trigger RSS feed ingestion
    rss_result = ingest_all_feeds.delay()

    # Trigger YouTube channel ingestion
    youtube_result = ingest_all_youtube_channels.delay()

    result = {
        "rss_task_id": rss_result.id,
        "youtube_task_id": youtube_result.id,
        "status": "queued",
        "timestamp": datetime.utcnow().isoformat()
    }

    logger.info("Queued comprehensive ingestion tasks")
    return result
