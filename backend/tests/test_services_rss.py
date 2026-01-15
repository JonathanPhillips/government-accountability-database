"""Tests for RSS ingestion service."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import feedparser

from app.services.rss_ingester import RSSIngester
from app.models.base import SourceTypeEnum


class TestRSSIngester:
    """Test suite for RSSIngester service."""

    def test_fetch_feed_success(self):
        """Test successful RSS feed fetching."""
        mock_feed = MagicMock()
        mock_feed.bozo = False
        mock_feed.feed = {
            'title': 'Test Feed',
            'link': 'https://example.com',
            'description': 'Test Description'
        }
        mock_feed.entries = [
            {'title': 'Entry 1', 'link': 'https://example.com/1'},
            {'title': 'Entry 2', 'link': 'https://example.com/2'}
        ]

        with patch('feedparser.parse', return_value=mock_feed):
            result = RSSIngester.fetch_feed('https://example.com/feed')

            assert result['title'] == 'Test Feed'
            assert result['link'] == 'https://example.com'
            assert len(result['entries']) == 2

    def test_fetch_feed_invalid(self):
        """Test fetching an invalid RSS feed."""
        mock_feed = MagicMock()
        mock_feed.bozo = True
        mock_feed.bozo_exception = Exception("Invalid XML")

        with patch('feedparser.parse', return_value=mock_feed):
            with pytest.raises(Exception, match="Invalid feed"):
                RSSIngester.fetch_feed('https://example.com/invalid')

    def test_extract_article_content_with_article_tag(self):
        """Test content extraction with article tag."""
        mock_response = Mock()
        mock_response.content = b"""
            <html>
                <article>
                    <p>Test article content</p>
                </article>
            </html>
        """

        with patch('requests.get', return_value=mock_response):
            content = RSSIngester.extract_article_content('https://example.com/article')

            assert content is not None
            assert 'Test article content' in content

    def test_extract_article_content_with_main_tag(self):
        """Test content extraction with main tag (no article tag)."""
        mock_response = Mock()
        mock_response.content = b"""
            <html>
                <main>
                    <p>Test main content</p>
                </main>
            </html>
        """

        with patch('requests.get', return_value=mock_response):
            content = RSSIngester.extract_article_content('https://example.com/article')

            assert content is not None
            assert 'Test main content' in content

    def test_extract_article_content_with_paragraphs(self):
        """Test content extraction fallback to paragraphs."""
        mock_response = Mock()
        mock_response.content = b"""
            <html>
                <body>
                    <p>First paragraph</p>
                    <p>Second paragraph</p>
                </body>
            </html>
        """

        with patch('requests.get', return_value=mock_response):
            content = RSSIngester.extract_article_content('https://example.com/article')

            assert content is not None
            assert 'First paragraph' in content
            assert 'Second paragraph' in content

    def test_extract_article_content_request_fails(self):
        """Test content extraction when HTTP request fails."""
        with patch('requests.get', side_effect=Exception("Network error")):
            content = RSSIngester.extract_article_content('https://example.com/article')

            assert content is None

    def test_parse_entry_date_with_published(self):
        """Test date parsing with published_parsed field."""
        mock_entry = Mock()
        mock_entry.published_parsed = (2024, 1, 15, 12, 30, 0, 0, 0, 0)

        date = RSSIngester.parse_entry_date(mock_entry)

        assert date is not None
        assert date.year == 2024
        assert date.month == 1
        assert date.day == 15

    def test_parse_entry_date_with_updated(self):
        """Test date parsing with updated_parsed field (no published)."""
        mock_entry = Mock()
        mock_entry.updated_parsed = (2024, 1, 15, 12, 30, 0, 0, 0, 0)
        delattr(mock_entry, 'published_parsed')

        date = RSSIngester.parse_entry_date(mock_entry)

        assert date is not None
        assert date.year == 2024
        assert date.month == 1
        assert date.day == 15

    def test_parse_entry_date_no_date(self):
        """Test date parsing when no date fields present."""
        mock_entry = Mock()
        delattr(mock_entry, 'published_parsed')
        delattr(mock_entry, 'updated_parsed')
        delattr(mock_entry, 'created_parsed')

        date = RSSIngester.parse_entry_date(mock_entry)

        assert date is None

    def test_parse_entry_date_invalid_tuple(self):
        """Test date parsing with invalid date tuple."""
        mock_entry = Mock()
        mock_entry.published_parsed = ('invalid', 'data', 'here')

        date = RSSIngester.parse_entry_date(mock_entry)

        # Should return None after trying and failing
        assert date is None

    def test_add_to_queue(self, db_session):
        """Test adding an RSS entry to ingestion queue."""
        mock_entry = {
            'title': 'Test Article',
            'link': 'https://example.com/article',
            'summary': 'Test summary content',
            'author': 'Test Author',
            'tags': [{'term': 'tag1'}, {'term': 'tag2'}]
        }
        mock_entry_obj = Mock()
        mock_entry_obj.published_parsed = (2024, 1, 15, 12, 30, 0, 0, 0, 0)

        # Merge mock_entry dict into mock_entry_obj
        for key, value in mock_entry.items():
            setattr(mock_entry_obj, key, value)

        with patch.object(RSSIngester, 'extract_article_content', return_value=None):
            queue_item = RSSIngester.add_to_queue(
                db=db_session,
                feed_url='https://example.com/feed',
                entry=mock_entry_obj,
                source_type=SourceTypeEnum.NEWS_PRIMARY
            )

            assert queue_item.source_url == 'https://example.com/article'
            assert queue_item.source_type == SourceTypeEnum.NEWS_PRIMARY
            assert queue_item.extracted_data['title'] == 'Test Article'
            assert queue_item.extracted_data['author'] == 'Test Author'
            assert 'tag1' in queue_item.extracted_data['tags']

    def test_ingest_feed(self, db_session):
        """Test complete feed ingestion process."""
        mock_feed_data = {
            'title': 'Test Feed',
            'link': 'https://example.com',
            'description': 'Test Feed Description',
            'entries': []
        }

        # Create mock entries
        for i in range(3):
            entry = Mock()
            entry.title = f'Article {i+1}'
            entry.link = f'https://example.com/article{i+1}'
            entry.summary = f'Summary {i+1}'
            entry.author = 'Test Author'
            entry.tags = []
            entry.published_parsed = (2024, 1, 15+i, 12, 30, 0, 0, 0, 0)
            mock_feed_data['entries'].append(entry)

        with patch.object(RSSIngester, 'fetch_feed', return_value=mock_feed_data):
            with patch.object(RSSIngester, 'extract_article_content', return_value=None):
                queue_items = RSSIngester.ingest_feed(
                    db=db_session,
                    feed_url='https://example.com/feed',
                    source_type=SourceTypeEnum.NEWS_PRIMARY,
                    max_entries=2
                )

                # Should only ingest first 2 entries due to max_entries
                assert len(queue_items) == 2
                assert queue_items[0].extracted_data['title'] == 'Article 1'
                assert queue_items[1].extracted_data['title'] == 'Article 2'

    def test_ingest_feed_with_errors(self, db_session):
        """Test feed ingestion continues after individual entry errors."""
        mock_feed_data = {
            'title': 'Test Feed',
            'entries': []
        }

        # Create 3 entries, middle one will fail
        for i in range(3):
            entry = Mock()
            entry.title = f'Article {i+1}'
            entry.link = f'https://example.com/article{i+1}'
            entry.summary = f'Summary {i+1}'
            entry.author = 'Test Author'
            entry.tags = []
            entry.published_parsed = (2024, 1, 15+i, 12, 30, 0, 0, 0, 0)
            mock_feed_data['entries'].append(entry)

        def mock_add_to_queue(db, feed_url, entry, source_type):
            if 'Article 2' in entry.title:
                raise Exception("Database error")
            # Create a real queue item for successful entries
            from app.models import IngestionQueue
            return IngestionQueue(
                source_url=entry.link,
                source_type=source_type,
                raw_content=entry.summary,
                extracted_data={'title': entry.title}
            )

        with patch.object(RSSIngester, 'fetch_feed', return_value=mock_feed_data):
            with patch.object(RSSIngester, 'extract_article_content', return_value=None):
                with patch.object(RSSIngester, 'add_to_queue', side_effect=mock_add_to_queue):
                    queue_items = RSSIngester.ingest_feed(
                        db=db_session,
                        feed_url='https://example.com/feed',
                        source_type=SourceTypeEnum.NEWS_PRIMARY
                    )

                    # Should have 2 successful entries (1 and 3), skipping failed entry 2
                    assert len(queue_items) == 2
                    assert queue_items[0].extracted_data['title'] == 'Article 1'
                    assert queue_items[1].extracted_data['title'] == 'Article 3'
