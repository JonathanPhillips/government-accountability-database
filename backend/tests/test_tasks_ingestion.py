"""Tests for Celery ingestion tasks."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

from app.tasks.ingestion_tasks import (
    ingest_rss_feed,
    ingest_all_feeds,
    ingest_youtube_channel,
    ingest_all_youtube_channels,
    ingest_all_sources,
    cleanup_old_queue_items,
    RSS_FEED_SOURCES,
    YOUTUBE_CHANNEL_SOURCES
)
from app.models import IngestionQueue
from app.models.base import SourceTypeEnum, IngestionStatusEnum


class TestIngestRSSFeed:
    """Test suite for RSS feed ingestion task."""

    def test_ingest_rss_feed_success(self, db_session):
        """Test successful RSS feed ingestion."""
        feed_url = "https://example.com/feed"
        source_type = SourceTypeEnum.NEWS_PRIMARY.value

        # Create mock queue items
        mock_items = [
            Mock(spec=IngestionQueue),
            Mock(spec=IngestionQueue)
        ]

        with patch('app.tasks.ingestion_tasks.SessionLocal', return_value=db_session):
            with patch('app.tasks.ingestion_tasks.RSSIngester.ingest_feed',
                      return_value=mock_items):
                result = ingest_rss_feed(
                    feed_url=feed_url,
                    source_type=source_type,
                    max_entries=10
                )

                assert result['status'] == 'success'
                assert result['feed_url'] == feed_url
                assert result['entries_added'] == 2

    def test_ingest_rss_feed_failure(self, db_session):
        """Test RSS feed ingestion with failure."""
        feed_url = "https://example.com/feed"
        source_type = SourceTypeEnum.NEWS_PRIMARY.value

        # Create a mock task object to simulate Celery task behavior
        mock_task = Mock()
        mock_task.request = Mock()
        mock_task.request.retries = 0
        mock_task.MaxRetriesExceededError = Exception

        with patch('app.tasks.ingestion_tasks.SessionLocal', return_value=db_session):
            with patch('app.tasks.ingestion_tasks.RSSIngester.ingest_feed',
                      side_effect=Exception("Feed parse error")):
                # Mock the retry to raise MaxRetriesExceededError immediately
                mock_task.retry.side_effect = mock_task.MaxRetriesExceededError

                # Bind the task to the mock
                with patch.object(ingest_rss_feed, '__self__', mock_task):
                    result = ingest_rss_feed.__get__(mock_task, type(mock_task))(
                        feed_url=feed_url,
                        source_type=source_type
                    )

                    assert result['status'] == 'failed'
                    assert result['entries_added'] == 0
                    assert 'error' in result


class TestIngestAllFeeds:
    """Test suite for bulk RSS feed ingestion task."""

    def test_ingest_all_feeds_success(self):
        """Test successful ingestion of all configured feeds."""
        mock_task_result = Mock()
        mock_task_result.id = 'task-123'

        with patch('app.tasks.ingestion_tasks.ingest_rss_feed.delay',
                  return_value=mock_task_result) as mock_delay:
            results = ingest_all_feeds()

            # Should queue a task for each configured feed
            assert len(results) == len(RSS_FEED_SOURCES)
            assert all(r['status'] == 'queued' for r in results)
            assert mock_delay.call_count == len(RSS_FEED_SOURCES)

    def test_ingest_all_feeds_handles_errors(self):
        """Test bulk ingestion handles individual feed errors gracefully."""
        def mock_delay_with_error(**kwargs):
            if 'propublica' in kwargs['feed_url']:
                raise Exception("Network error")
            mock_result = Mock()
            mock_result.id = 'task-123'
            return mock_result

        with patch('app.tasks.ingestion_tasks.ingest_rss_feed.delay',
                  side_effect=mock_delay_with_error):
            results = ingest_all_feeds()

            # Should still return results for all feeds
            assert len(results) == len(RSS_FEED_SOURCES)

            # Some should be queued, some should have errors
            queued = [r for r in results if r['status'] == 'queued']
            errors = [r for r in results if r['status'] == 'error']

            assert len(queued) > 0
            assert len(errors) > 0


class TestIngestYouTubeChannel:
    """Test suite for YouTube channel ingestion task."""

    def test_ingest_youtube_channel_with_channel_id(self, db_session):
        """Test YouTube channel ingestion using channel ID."""
        channel_id = "UCxxxxxxxxxxxxx"
        name = "Test Channel"
        source_type = SourceTypeEnum.VIDEO.value

        mock_items = [Mock(spec=IngestionQueue)]

        with patch('app.tasks.ingestion_tasks.SessionLocal', return_value=db_session):
            with patch('app.tasks.ingestion_tasks.YouTubeIngester.get_channel_feed_url',
                      return_value='https://youtube.com/feeds/videos.xml?channel_id=UC123'):
                with patch('app.tasks.ingestion_tasks.RSSIngester.ingest_feed',
                          return_value=mock_items):
                    result = ingest_youtube_channel(
                        channel_id=channel_id,
                        name=name,
                        source_type=source_type,
                        max_videos=5
                    )

                    assert result['status'] == 'success'
                    assert result['channel'] == name
                    assert result['videos_added'] == 1

    def test_ingest_youtube_channel_with_username(self, db_session):
        """Test YouTube channel ingestion using username."""
        username = "testchannel"
        source_type = SourceTypeEnum.VIDEO.value

        mock_items = [Mock(spec=IngestionQueue)]

        with patch('app.tasks.ingestion_tasks.SessionLocal', return_value=db_session):
            with patch('app.tasks.ingestion_tasks.YouTubeIngester.get_channel_feed_url_by_username',
                      return_value='https://youtube.com/feeds/videos.xml?user=testchannel'):
                with patch('app.tasks.ingestion_tasks.RSSIngester.ingest_feed',
                          return_value=mock_items):
                    result = ingest_youtube_channel(
                        username=username,
                        source_type=source_type,
                        max_videos=5
                    )

                    assert result['status'] == 'success'
                    assert result['videos_added'] == 1

    def test_ingest_youtube_channel_no_identifier(self, db_session):
        """Test YouTube channel ingestion without channel ID or username."""
        with patch('app.tasks.ingestion_tasks.SessionLocal', return_value=db_session):
            # Create mock task
            mock_task = Mock()
            mock_task.request = Mock()
            mock_task.request.retries = 0
            mock_task.MaxRetriesExceededError = Exception

            with patch.object(ingest_youtube_channel, '__self__', mock_task):
                result = ingest_youtube_channel.__get__(mock_task, type(mock_task))(
                    source_type=SourceTypeEnum.VIDEO.value
                )

                assert result['status'] == 'failed'
                assert 'error' in result


class TestIngestAllYouTubeChannels:
    """Test suite for bulk YouTube channel ingestion task."""

    def test_ingest_all_youtube_channels_success(self):
        """Test successful ingestion of all configured channels."""
        mock_task_result = Mock()
        mock_task_result.id = 'task-456'

        with patch('app.tasks.ingestion_tasks.ingest_youtube_channel.delay',
                  return_value=mock_task_result) as mock_delay:
            results = ingest_all_youtube_channels()

            # Should queue a task for each configured channel
            assert len(results) == len(YOUTUBE_CHANNEL_SOURCES)
            assert all(r['status'] == 'queued' for r in results)
            assert mock_delay.call_count == len(YOUTUBE_CHANNEL_SOURCES)


class TestIngestAllSources:
    """Test suite for comprehensive ingestion task."""

    def test_ingest_all_sources(self):
        """Test triggering ingestion from all source types."""
        mock_rss_result = Mock()
        mock_rss_result.id = 'rss-task-123'

        mock_youtube_result = Mock()
        mock_youtube_result.id = 'youtube-task-456'

        with patch('app.tasks.ingestion_tasks.ingest_all_feeds.delay',
                  return_value=mock_rss_result):
            with patch('app.tasks.ingestion_tasks.ingest_all_youtube_channels.delay',
                      return_value=mock_youtube_result):
                result = ingest_all_sources()

                assert result['status'] == 'queued'
                assert result['rss_task_id'] == 'rss-task-123'
                assert result['youtube_task_id'] == 'youtube-task-456'
                assert 'timestamp' in result


class TestCleanupOldQueueItems:
    """Test suite for queue cleanup task."""

    def test_cleanup_old_queue_items_success(self, db_session):
        """Test successful cleanup of old queue items."""
        # Create some old processed items
        old_date = datetime.utcnow() - timedelta(days=35)

        for i in range(3):
            item = IngestionQueue(
                source_url=f"https://example.com/{i}",
                source_type=SourceTypeEnum.NEWS_PRIMARY,
                raw_content="Test content",
                status=IngestionStatusEnum.APPROVED,
                extracted_data={}
            )
            item.updated_at = old_date
            db_session.add(item)

        # Create some recent items that should not be deleted
        for i in range(2):
            item = IngestionQueue(
                source_url=f"https://example.com/recent-{i}",
                source_type=SourceTypeEnum.NEWS_PRIMARY,
                raw_content="Test content",
                status=IngestionStatusEnum.APPROVED,
                extracted_data={}
            )
            db_session.add(item)

        db_session.commit()

        with patch('app.tasks.ingestion_tasks.SessionLocal', return_value=db_session):
            result = cleanup_old_queue_items(days=30)

            assert result['status'] == 'success'
            assert result['deleted_count'] == 3

            # Verify recent items still exist
            remaining_items = db_session.query(IngestionQueue).filter(
                IngestionQueue.status == IngestionStatusEnum.APPROVED
            ).all()
            assert len(remaining_items) == 2

    def test_cleanup_does_not_delete_pending_items(self, db_session):
        """Test cleanup doesn't delete pending items even if old."""
        old_date = datetime.utcnow() - timedelta(days=35)

        # Create old pending item
        item = IngestionQueue(
            source_url="https://example.com/pending",
            source_type=SourceTypeEnum.NEWS_PRIMARY,
            raw_content="Test content",
            status=IngestionStatusEnum.PENDING,
            extracted_data={}
        )
        item.updated_at = old_date
        db_session.add(item)
        db_session.commit()

        with patch('app.tasks.ingestion_tasks.SessionLocal', return_value=db_session):
            result = cleanup_old_queue_items(days=30)

            # Should not delete pending items
            assert result['deleted_count'] == 0

            # Verify pending item still exists
            remaining = db_session.query(IngestionQueue).filter(
                IngestionQueue.status == IngestionStatusEnum.PENDING
            ).all()
            assert len(remaining) == 1

    def test_cleanup_old_queue_items_error_handling(self, db_session):
        """Test cleanup task handles database errors gracefully."""
        with patch('app.tasks.ingestion_tasks.SessionLocal', return_value=db_session):
            # Mock the query to raise an error
            with patch.object(db_session, 'query', side_effect=Exception("Database error")):
                result = cleanup_old_queue_items(days=30)

                assert result['status'] == 'failed'
                assert 'error' in result
                assert result['deleted_count'] == 0
