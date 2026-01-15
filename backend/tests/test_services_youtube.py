"""Tests for YouTube ingestion service."""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from app.services.youtube_ingester import YouTubeIngester
from app.models.base import SourceTypeEnum


class TestYouTubeIngester:
    """Test suite for YouTubeIngester service."""

    def test_extract_video_id_from_watch_url(self):
        """Test video ID extraction from standard watch URL."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        video_id = YouTubeIngester.extract_video_id(url)

        assert video_id == "dQw4w9WgXcQ"

    def test_extract_video_id_from_short_url(self):
        """Test video ID extraction from youtu.be short URL."""
        url = "https://youtu.be/dQw4w9WgXcQ"
        video_id = YouTubeIngester.extract_video_id(url)

        assert video_id == "dQw4w9WgXcQ"

    def test_extract_video_id_from_embed_url(self):
        """Test video ID extraction from embed URL."""
        url = "https://www.youtube.com/embed/dQw4w9WgXcQ"
        video_id = YouTubeIngester.extract_video_id(url)

        assert video_id == "dQw4w9WgXcQ"

    def test_extract_video_id_from_v_url(self):
        """Test video ID extraction from /v/ URL."""
        url = "https://www.youtube.com/v/dQw4w9WgXcQ"
        video_id = YouTubeIngester.extract_video_id(url)

        assert video_id == "dQw4w9WgXcQ"

    def test_extract_video_id_with_additional_params(self):
        """Test video ID extraction with additional URL parameters."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ&feature=share&t=30s"
        video_id = YouTubeIngester.extract_video_id(url)

        assert video_id == "dQw4w9WgXcQ"

    def test_extract_video_id_invalid_url(self):
        """Test video ID extraction from invalid URL."""
        url = "https://example.com/not-a-youtube-url"
        video_id = YouTubeIngester.extract_video_id(url)

        assert video_id is None

    def test_get_transcript_success(self):
        """Test successful transcript fetching."""
        mock_transcript = [
            {'start': 0.0, 'text': 'Hello world'},
            {'start': 2.5, 'text': 'This is a test'},
            {'start': 5.0, 'text': 'Transcript content'}
        ]

        with patch('app.services.youtube_ingester.YouTubeTranscriptApi.get_transcript',
                   return_value=mock_transcript):
            transcript = YouTubeIngester.get_transcript('dQw4w9WgXcQ')

            assert transcript is not None
            assert 'Hello world' in transcript
            assert '[0.0s]' in transcript
            assert '[2.5s]' in transcript
            assert 'This is a test' in transcript

    def test_get_transcript_not_available(self):
        """Test transcript fetching when transcript not available."""
        with patch('app.services.youtube_ingester.YouTubeTranscriptApi.get_transcript',
                   side_effect=Exception("Transcript not available")):
            transcript = YouTubeIngester.get_transcript('invalid_id')

            assert transcript is None

    def test_get_transcript_custom_language(self):
        """Test transcript fetching with custom language."""
        mock_transcript = [
            {'start': 0.0, 'text': 'Hola mundo'}
        ]

        with patch('app.services.youtube_ingester.YouTubeTranscriptApi.get_transcript',
                   return_value=mock_transcript) as mock_get:
            transcript = YouTubeIngester.get_transcript('dQw4w9WgXcQ', languages=['es'])

            assert transcript is not None
            assert 'Hola mundo' in transcript
            # Verify the language parameter was passed
            mock_get.assert_called_once_with('dQw4w9WgXcQ', languages=['es'])

    def test_get_video_info(self):
        """Test getting basic video information."""
        video_info = YouTubeIngester.get_video_info('dQw4w9WgXcQ')

        assert video_info['video_id'] == 'dQw4w9WgXcQ'
        assert video_info['url'] == 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
        assert video_info['embed_url'] == 'https://www.youtube.com/embed/dQw4w9WgXcQ'

    def test_get_channel_feed_url(self):
        """Test getting RSS feed URL for a YouTube channel."""
        channel_id = "UCxxxxxxxxxxxxx"
        feed_url = YouTubeIngester.get_channel_feed_url(channel_id)

        assert feed_url == f'https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}'

    def test_get_channel_feed_url_by_username(self):
        """Test getting RSS feed URL for a YouTube channel by username."""
        username = "testchannel"
        feed_url = YouTubeIngester.get_channel_feed_url_by_username(username)

        assert feed_url == f'https://www.youtube.com/feeds/videos.xml?user={username}'

    def test_get_channel_feed_url_by_username_with_at_symbol(self):
        """Test getting RSS feed URL when username has @ symbol."""
        username = "@testchannel"
        feed_url = YouTubeIngester.get_channel_feed_url_by_username(username)

        # @ should be stripped
        assert feed_url == 'https://www.youtube.com/feeds/videos.xml?user=testchannel'

    def test_add_to_queue(self, db_session):
        """Test adding a YouTube video to ingestion queue."""
        video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        title = "Test Video"
        transcript = "[0.0s] Test transcript content"
        author = "Test Author"
        pub_date = datetime(2024, 1, 15, 12, 30, 0)

        queue_item = YouTubeIngester.add_to_queue(
            db=db_session,
            video_url=video_url,
            title=title,
            transcript=transcript,
            author=author,
            published_date=pub_date
        )

        assert queue_item.source_url == video_url
        assert queue_item.source_type == SourceTypeEnum.VIDEO
        assert queue_item.raw_content == transcript
        assert queue_item.extracted_data['title'] == title
        assert queue_item.extracted_data['author'] == author
        assert queue_item.extracted_data['video_id'] == 'dQw4w9WgXcQ'
        assert queue_item.extracted_data['platform'] == 'youtube'

    def test_add_to_queue_invalid_url(self, db_session):
        """Test adding video with invalid URL raises error."""
        invalid_url = "https://example.com/not-youtube"

        with pytest.raises(ValueError, match="Invalid YouTube URL"):
            YouTubeIngester.add_to_queue(
                db=db_session,
                video_url=invalid_url,
                title="Test",
                transcript="Test transcript"
            )

    def test_add_to_queue_with_metadata(self, db_session):
        """Test adding video with additional metadata."""
        video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        metadata = {
            'duration': '3:45',
            'views': 1000000,
            'channel': 'Test Channel'
        }

        queue_item = YouTubeIngester.add_to_queue(
            db=db_session,
            video_url=video_url,
            title="Test Video",
            transcript="Test transcript",
            metadata=metadata
        )

        assert queue_item.extracted_data['duration'] == '3:45'
        assert queue_item.extracted_data['views'] == 1000000
        assert queue_item.extracted_data['channel'] == 'Test Channel'

    def test_ingest_video_success(self, db_session):
        """Test complete video ingestion process."""
        video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        title = "Test Video"
        author = "Test Author"
        pub_date = datetime(2024, 1, 15, 12, 30, 0)

        mock_transcript = [
            {'start': 0.0, 'text': 'Test content'}
        ]

        with patch('app.services.youtube_ingester.YouTubeTranscriptApi.get_transcript',
                   return_value=mock_transcript):
            queue_item = YouTubeIngester.ingest_video(
                db=db_session,
                video_url=video_url,
                title=title,
                author=author,
                published_date=pub_date
            )

            assert queue_item is not None
            assert queue_item.source_url == video_url
            assert queue_item.extracted_data['title'] == title
            assert 'Test content' in queue_item.raw_content

    def test_ingest_video_invalid_url(self, db_session):
        """Test video ingestion with invalid URL."""
        invalid_url = "https://example.com/not-youtube"

        with pytest.raises(ValueError, match="Invalid YouTube URL"):
            YouTubeIngester.ingest_video(
                db=db_session,
                video_url=invalid_url,
                title="Test"
            )

    def test_ingest_video_transcript_not_available(self, db_session):
        """Test video ingestion when transcript is not available."""
        video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

        with patch('app.services.youtube_ingester.YouTubeTranscriptApi.get_transcript',
                   return_value=None) as mock_get:
            with pytest.raises(Exception, match="Could not fetch transcript"):
                YouTubeIngester.ingest_video(
                    db=db_session,
                    video_url=video_url,
                    title="Test Video"
                )

    def test_ingest_video_custom_languages(self, db_session):
        """Test video ingestion with custom language preferences."""
        video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        mock_transcript = [
            {'start': 0.0, 'text': 'Contenido de prueba'}
        ]

        with patch('app.services.youtube_ingester.YouTubeTranscriptApi.get_transcript',
                   return_value=mock_transcript) as mock_get:
            queue_item = YouTubeIngester.ingest_video(
                db=db_session,
                video_url=video_url,
                title="Test Video",
                languages=['es', 'en']
            )

            assert queue_item is not None
            # Verify custom languages were passed
            mock_get.assert_called_once_with('dQw4w9WgXcQ', ['es', 'en'])
