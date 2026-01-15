"""RSS feed ingestion service."""
import feedparser
import requests
from datetime import datetime
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

from app.models import IngestionQueue
from app.models.base import SourceTypeEnum


class RSSIngester:
    """Service for ingesting RSS feeds."""

    @staticmethod
    def fetch_feed(feed_url: str) -> Dict:
        """Fetch and parse RSS feed."""
        try:
            feed = feedparser.parse(feed_url)

            if feed.bozo:
                raise ValueError(f"Invalid feed: {feed.bozo_exception}")

            return {
                'title': feed.feed.get('title', ''),
                'link': feed.feed.get('link', ''),
                'description': feed.feed.get('description', ''),
                'entries': feed.entries
            }
        except Exception as e:
            raise Exception(f"Failed to fetch RSS feed: {str(e)}")

    @staticmethod
    def extract_article_content(url: str) -> Optional[str]:
        """Extract main content from article URL."""
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()

            # Try to find article content
            article = soup.find('article')
            if article:
                return article.get_text(separator='\n', strip=True)

            # Fallback to main content
            main = soup.find('main')
            if main:
                return main.get_text(separator='\n', strip=True)

            # Last resort - get all paragraphs
            paragraphs = soup.find_all('p')
            if paragraphs:
                return '\n\n'.join(p.get_text(strip=True) for p in paragraphs)

            return None
        except Exception as e:
            print(f"Error extracting content from {url}: {str(e)}")
            return None

    @staticmethod
    def parse_entry_date(entry) -> Optional[datetime]:
        """Parse publication date from feed entry."""
        date_fields = ['published_parsed', 'updated_parsed', 'created_parsed']

        for field in date_fields:
            if hasattr(entry, field):
                date_tuple = getattr(entry, field)
                if date_tuple:
                    try:
                        return datetime(*date_tuple[:6])
                    except:
                        pass

        return None

    @staticmethod
    def add_to_queue(
        db: Session,
        feed_url: str,
        entry: Dict,
        source_type: SourceTypeEnum = SourceTypeEnum.NEWS_PRIMARY
    ) -> IngestionQueue:
        """Add feed entry to ingestion queue."""
        # Parse date
        pub_date = RSSIngester.parse_entry_date(entry)

        # Extract content
        content = entry.get('summary', '')
        full_url = entry.get('link', '')

        # Try to get full article content
        if full_url:
            full_content = RSSIngester.extract_article_content(full_url)
            if full_content and len(full_content) > len(content):
                content = full_content

        # Create queue item with correct field structure
        queue_item = IngestionQueue(
            source_url=full_url,
            source_type=source_type,
            raw_content=content,
            extracted_data={
                'title': entry.get('title', ''),
                'author': entry.get('author', None),
                'published_date': pub_date.isoformat() if pub_date else None,
                'feed_url': feed_url,
                'feed_title': entry.get('source', {}).get('title', ''),
                'tags': [tag.get('term', '') for tag in entry.get('tags', [])]
            }
        )

        db.add(queue_item)
        db.commit()
        db.refresh(queue_item)

        return queue_item

    @staticmethod
    def ingest_feed(
        db: Session,
        feed_url: str,
        source_type: SourceTypeEnum = SourceTypeEnum.NEWS_PRIMARY,
        max_entries: Optional[int] = None
    ) -> List[IngestionQueue]:
        """Ingest RSS feed and add entries to queue."""
        feed_data = RSSIngester.fetch_feed(feed_url)
        entries = feed_data['entries']

        if max_entries:
            entries = entries[:max_entries]

        queue_items = []
        for entry in entries:
            try:
                queue_item = RSSIngester.add_to_queue(
                    db=db,
                    feed_url=feed_url,
                    entry=entry,
                    source_type=source_type
                )
                queue_items.append(queue_item)
            except Exception as e:
                print(f"Error adding entry to queue: {str(e)}")
                continue

        return queue_items
