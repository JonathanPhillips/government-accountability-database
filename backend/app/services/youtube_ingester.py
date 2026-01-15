"""YouTube video ingestion service."""
import re
import logging
from typing import Optional, Dict
from datetime import datetime
from youtube_transcript_api import YouTubeTranscriptApi
from sqlalchemy.orm import Session

from app.models import IngestionQueue
from app.models.base import SourceTypeEnum

logger = logging.getLogger(__name__)


class YouTubeIngester:
    """Service for ingesting YouTube video transcripts."""

    @staticmethod
    def extract_video_id(url: str) -> Optional[str]:
        """Extract video ID from YouTube URL."""
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?]*)',
            r'youtube\.com\/embed\/([^&\n?]*)',
            r'youtube\.com\/v\/([^&\n?]*)'
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)

        return None

    @staticmethod
    def get_transcript(video_id: str, languages: list = ['en']) -> Optional[str]:
        """Fetch transcript for YouTube video."""
        try:
            transcript_list = YouTubeTranscriptApi.get_transcript(
                video_id,
                languages=languages
            )

            # Combine transcript segments
            transcript = '\n'.join([
                f"[{entry['start']:.1f}s] {entry['text']}"
                for entry in transcript_list
            ])

            return transcript
        except Exception as e:
            logger.error(f"Error fetching transcript for {video_id}: {str(e)}", exc_info=True)
            return None

    @staticmethod
    def get_video_info(video_id: str) -> Dict:
        """Get basic video information."""
        # Note: For production, you'd want to use YouTube Data API
        # This is a simplified version
        return {
            'video_id': video_id,
            'url': f'https://www.youtube.com/watch?v={video_id}',
            'embed_url': f'https://www.youtube.com/embed/{video_id}'
        }

    @staticmethod
    def get_channel_feed_url(channel_id: str) -> str:
        """
        Get RSS feed URL for a YouTube channel.

        YouTube provides RSS feeds for channels that can be used
        to monitor new videos without API quota limits.

        Args:
            channel_id: YouTube channel ID (starts with UC...)

        Returns:
            RSS feed URL for the channel
        """
        return f'https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}'

    @staticmethod
    def get_channel_feed_url_by_username(username: str) -> str:
        """
        Get RSS feed URL for a YouTube channel by username.

        Args:
            username: YouTube channel username/handle (e.g., @username)

        Returns:
            RSS feed URL for the channel
        """
        # Remove @ if present
        username = username.lstrip('@')
        return f'https://www.youtube.com/feeds/videos.xml?user={username}'

    @staticmethod
    def add_to_queue(
        db: Session,
        video_url: str,
        title: str,
        transcript: str,
        author: Optional[str] = None,
        published_date: Optional[datetime] = None,
        metadata: Optional[Dict] = None
    ) -> IngestionQueue:
        """Add YouTube video to ingestion queue."""
        video_id = YouTubeIngester.extract_video_id(video_url)

        if not video_id:
            raise ValueError(f"Invalid YouTube URL: {video_url}")

        # Create queue item with correct field structure
        queue_item = IngestionQueue(
            source_url=video_url,
            source_type=SourceTypeEnum.VIDEO,
            raw_content=transcript,
            extracted_data={
                'title': title,
                'author': author,
                'published_date': published_date.isoformat() if published_date else None,
                'video_id': video_id,
                'platform': 'youtube',
                **(metadata or {})
            }
        )

        db.add(queue_item)
        db.commit()
        db.refresh(queue_item)

        return queue_item

    @staticmethod
    def ingest_video(
        db: Session,
        video_url: str,
        title: str,
        author: Optional[str] = None,
        published_date: Optional[datetime] = None,
        languages: list = ['en']
    ) -> Optional[IngestionQueue]:
        """Ingest YouTube video and add to queue."""
        video_id = YouTubeIngester.extract_video_id(video_url)

        if not video_id:
            raise ValueError(f"Invalid YouTube URL: {video_url}")

        # Get transcript
        transcript = YouTubeIngester.get_transcript(video_id, languages)

        if not transcript:
            raise Exception(f"Could not fetch transcript for video {video_id}")

        # Get video info
        video_info = YouTubeIngester.get_video_info(video_id)

        # Add to queue
        return YouTubeIngester.add_to_queue(
            db=db,
            video_url=video_info['url'],
            title=title,
            transcript=transcript,
            author=author,
            published_date=published_date,
            metadata=video_info
        )
