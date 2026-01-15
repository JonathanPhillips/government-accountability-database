# Ingestion Sources Configuration

This document lists all configured ingestion sources for the Government Accountability Database.

## Overview

The GADB ingestion system automatically fetches content from multiple sources including:
- RSS feeds from news organizations and watchdog groups
- YouTube channels from investigative journalism organizations
- Manual entries via the admin interface

All automatically ingested content goes into the `ingestion_queue` table for human review before being added to the main database.

## RSS Feed Sources

### Configured Feeds

| Source | URL | Type | Update Frequency |
|--------|-----|------|------------------|
| ProPublica | https://www.propublica.org/feeds/propublica/main | NEWS_PRIMARY | Every 2 hours |
| The Intercept | https://theintercept.com/feed/ | NEWS_PRIMARY | Every 2 hours |
| BBC News - US & Canada | https://feeds.bbci.co.uk/news/world/us_and_canada/rss.xml | NEWS_SECONDARY | Every 2 hours |
| EFF Deeplinks | https://www.eff.org/rss/updates.xml | CIVIL_LIBERTIES | Every 2 hours |
| NPR Politics | https://feeds.npr.org/1014/rss.xml | NEWS_SECONDARY | Every 2 hours |

### RSS Feed Configuration

Located in: `backend/app/tasks/ingestion_tasks.py`

```python
RSS_FEED_SOURCES = [
    {
        "feed_url": "https://www.propublica.org/feeds/propublica/main",
        "source_type": SourceTypeEnum.NEWS_PRIMARY,
        "max_entries": 10
    },
    {
        "feed_url": "https://theintercept.com/feed/",
        "source_type": SourceTypeEnum.NEWS_PRIMARY,
        "max_entries": 10
    },
    {
        "feed_url": "https://feeds.bbci.co.uk/news/world/us_and_canada/rss.xml",
        "source_type": SourceTypeEnum.NEWS_SECONDARY,
        "max_entries": 10
    },
    {
        "feed_url": "https://www.eff.org/rss/updates.xml",
        "source_type": SourceTypeEnum.CIVIL_LIBERTIES,
        "max_entries": 10
    },
    {
        "feed_url": "https://feeds.npr.org/1014/rss.xml",
        "source_type": SourceTypeEnum.NEWS_SECONDARY,
        "max_entries": 10
    },
]
```

## YouTube Channel Sources

### Configured Channels

| Channel | Channel ID | Type | Videos Per Check |
|---------|-----------|------|------------------|
| ProPublica | UCe02lGcO-ahAURWuxAJnjdA | VIDEO | 5 |
| The Intercept | UCnMw7MmuZAwYGJK-r2KxLqQ | VIDEO | 5 |
| Electronic Frontier Foundation | UCKPZi7rFM5oy2Ln0Z8KJQ6w | VIDEO | 5 |
| Democracy Now! | UCJDn07DCtlBEYe8zQNkdzzQ | VIDEO | 5 |

### YouTube Channel Configuration

Located in: `backend/app/tasks/ingestion_tasks.py`

```python
YOUTUBE_CHANNEL_SOURCES = [
    {
        "channel_id": "UCe02lGcO-ahAURWuxAJnjdA",
        "name": "ProPublica",
        "source_type": SourceTypeEnum.VIDEO,
        "max_videos": 5
    },
    {
        "channel_id": "UCnMw7MmuZAwYGJK-r2KxLqQ",
        "name": "The Intercept",
        "source_type": SourceTypeEnum.VIDEO,
        "max_videos": 5
    },
    {
        "channel_id": "UCKPZi7rFM5oy2Ln0Z8KJQ6w",
        "name": "Electronic Frontier Foundation",
        "source_type": SourceTypeEnum.VIDEO,
        "max_videos": 5
    },
    {
        "channel_id": "UCJDn07DCtlBEYe8zQNkdzzQ",
        "name": "Democracy Now!",
        "source_type": SourceTypeEnum.VIDEO,
        "max_videos": 5
    },
]
```

### How YouTube Ingestion Works

YouTube channels are monitored using YouTube's RSS feeds, which:
- Don't require API keys or authentication
- Have no quota limits
- Update automatically when channels post new videos
- Include video metadata (title, description, publish date)

For each video, the system:
1. Extracts the video ID from the RSS feed
2. Attempts to fetch the video transcript using `youtube-transcript-api`
3. Creates an ingestion queue item with:
   - Video URL and metadata
   - Full transcript text
   - Channel information
   - Publication date

**Note**: Transcripts are only available for videos that have captions. Videos without transcripts will log a warning but won't break the ingestion process.

## Automated Ingestion Schedule

Located in: `backend/app/celerybeat_schedule.py`

### Active Schedules

| Task | Schedule | Description |
|------|----------|-------------|
| `ingest-all-feeds` | Every 2 hours (on the hour) | Ingest from all configured RSS feeds |
| `ingest-all-youtube-channels` | Every 4 hours (at :30 minutes) | Ingest from all configured YouTube channels |
| `ingest-all-sources-daily` | Daily at 3:00 AM | Comprehensive ingestion from all sources |
| `cleanup-old-queue-items` | Sundays at 2:00 AM | Remove processed items older than 30 days |

### Schedule Details

```python
CELERYBEAT_SCHEDULE = {
    'ingest-all-feeds': {
        'task': 'app.tasks.ingestion_tasks.ingest_all_feeds',
        'schedule': crontab(minute=0, hour='*/2'),
        'options': {'expires': 3600}
    },
    'ingest-all-youtube-channels': {
        'task': 'app.tasks.ingestion_tasks.ingest_all_youtube_channels',
        'schedule': crontab(minute=30, hour='*/4'),
        'options': {'expires': 3600}
    },
    'ingest-all-sources-daily': {
        'task': 'app.tasks.ingestion_tasks.ingest_all_sources',
        'schedule': crontab(hour=3, minute=0),
        'options': {'expires': 7200}
    },
    'cleanup-old-queue-items': {
        'task': 'app.tasks.ingestion_tasks.cleanup_old_queue_items',
        'schedule': crontab(day_of_week=0, hour=2, minute=0),
        'kwargs': {'days': 30},
        'options': {'expires': 3600}
    },
}
```

## Adding New Sources

### Adding an RSS Feed

1. Edit `backend/app/tasks/ingestion_tasks.py`
2. Add entry to `RSS_FEED_SOURCES` list:
   ```python
   {
       "feed_url": "https://example.com/feed.xml",
       "source_type": SourceTypeEnum.NEWS_PRIMARY,  # or NEWS_SECONDARY, CIVIL_LIBERTIES, etc.
       "max_entries": 10  # Number of most recent entries to fetch
   }
   ```
3. Restart Celery workers: `docker-compose restart celery-worker celery-beat`

### Adding a YouTube Channel

1. Get the channel ID:
   - Visit the channel page on YouTube
   - Channel ID is in the URL: `youtube.com/channel/CHANNEL_ID`
   - Or use username: `youtube.com/@username`

2. Edit `backend/app/tasks/ingestion_tasks.py`
3. Add entry to `YOUTUBE_CHANNEL_SOURCES` list:
   ```python
   {
       "channel_id": "UCxxxxxxxxxxxxx",  # or use "username": "@channelname"
       "name": "Channel Display Name",
       "source_type": SourceTypeEnum.VIDEO,
       "max_videos": 5  # Number of most recent videos to check
   }
   ```
4. Restart Celery workers: `docker-compose restart celery-worker celery-beat`

### Modifying the Schedule

1. Edit `backend/app/celerybeat_schedule.py`
2. Modify the `crontab()` expressions:
   - `crontab(minute=0, hour='*/2')` - Every 2 hours on the hour
   - `crontab(minute='*/30')` - Every 30 minutes
   - `crontab(hour=3, minute=0)` - Daily at 3:00 AM
   - `crontab(day_of_week=0, hour=2)` - Sundays at 2:00 AM
3. Restart Celery Beat: `docker-compose restart celery-beat`

## Manual Ingestion

### Via API (requires admin/editor role)

```bash
# Trigger RSS feed ingestion
curl -X POST http://localhost:8000/api/admin/ingest/rss \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "feed_url": "https://example.com/feed.xml",
    "source_type": "NEWS_PRIMARY",
    "max_entries": 10
  }'

# Trigger YouTube channel ingestion
curl -X POST http://localhost:8000/api/admin/ingest/youtube \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "channel_id": "UCxxxxxxxxxxxxx",
    "name": "Channel Name",
    "max_videos": 5
  }'
```

### Via Django Shell (if using manage.py)

```python
from app.tasks.ingestion_tasks import ingest_rss_feed, ingest_youtube_channel

# Ingest specific RSS feed
result = ingest_rss_feed.delay(
    feed_url="https://example.com/feed.xml",
    source_type="NEWS_PRIMARY",
    max_entries=10
)

# Ingest specific YouTube channel
result = ingest_youtube_channel.delay(
    channel_id="UCxxxxxxxxxxxxx",
    name="Channel Name",
    max_videos=5
)

# Check task status
print(result.status)
print(result.result)
```

## Monitoring Ingestion

### Check Celery Task Status

```bash
# View Celery worker logs
docker-compose logs -f celery-worker

# View Celery beat logs (scheduler)
docker-compose logs -f celery-beat

# Check Redis for task queue
docker exec -it gadb-redis redis-cli
> LLEN celery
```

### Check Ingestion Queue

```sql
-- View pending items awaiting review
SELECT
    id,
    source_url,
    source_type,
    status,
    created_at
FROM ingestion_queue
WHERE status = 'PENDING'
ORDER BY created_at DESC
LIMIT 20;

-- View statistics by source type
SELECT
    source_type,
    status,
    COUNT(*) as count
FROM ingestion_queue
GROUP BY source_type, status;
```

### Monitor via API

```bash
# Get ingestion queue statistics (requires authentication)
curl http://localhost:8000/api/admin/ingestion/stats \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# List pending items for review
curl http://localhost:8000/api/admin/ingestion/queue?status=PENDING \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Troubleshooting

### RSS Feed Ingestion Fails

**Problem**: Feed returns HTTP errors or parsing fails

**Solutions**:
1. Check feed URL is accessible: `curl -I https://example.com/feed.xml`
2. Verify feed is valid XML/RSS: Use https://validator.w3.org/feed/
3. Check Celery worker logs for specific errors
4. Ensure `feedparser` is installed: `pip install feedparser`

### YouTube Transcript Unavailable

**Problem**: Videos ingest but transcripts are missing

**Solutions**:
1. Verify video has captions/subtitles enabled
2. Check `youtube-transcript-api` is installed: `pip install youtube-transcript-api`
3. Try different language codes: `languages=['en', 'en-US', 'en-GB']`
4. Some videos may not have captions (expected behavior)

### Celery Tasks Not Running

**Problem**: Scheduled tasks don't execute

**Solutions**:
1. Verify Redis is running: `docker-compose ps redis`
2. Check Celery worker is connected: `docker-compose logs celery-worker`
3. Verify Celery beat is running: `docker-compose logs celery-beat`
4. Check schedule is loaded: `docker exec -it gadb-celery-worker celery -A app.celery_app inspect scheduled`

### Ingestion Queue Growing Too Large

**Problem**: Queue has thousands of pending items

**Solutions**:
1. Increase review frequency (assign more reviewers)
2. Adjust `max_entries` and `max_videos` to fetch fewer items per source
3. Run cleanup task manually: `cleanup_old_queue_items.delay(days=30)`
4. Consider adding filters to ingestion (e.g., date ranges, keywords)

## Source Type Definitions

| Type | Description | Use Case |
|------|-------------|----------|
| `NEWS_PRIMARY` | Primary news sources | Major investigative journalism outlets |
| `NEWS_SECONDARY` | Secondary news sources | General news with occasional accountability coverage |
| `CIVIL_LIBERTIES` | Civil liberties organizations | EFF, ACLU, civil rights groups |
| `VIDEO` | Video content | YouTube channels, video journalism |
| `GOVERNMENT_DOCUMENT` | Official documents | FOIA releases, official reports |
| `COURT_DOCUMENT` | Legal filings | Court records, legal documents |
| `RESEARCH_PAPER` | Academic research | Studies, reports, white papers |
| `SOCIAL_MEDIA` | Social media posts | Twitter threads, Facebook posts (future) |

## Best Practices

### Source Selection Criteria

Choose sources that:
- Have editorial standards and fact-checking
- Focus on government accountability and transparency
- Provide primary source citations
- Have consistent publishing schedules
- Cover a diverse range of topics (federal, state, local government)

### Ingestion Configuration

- **max_entries / max_videos**: Set to 5-10 to avoid overwhelming reviewers
- **Schedule frequency**: Balance between timeliness and reviewer capacity
- **Source types**: Use appropriate types for accurate categorization
- **Cleanup frequency**: Run weekly to keep database size manageable

### Review Process

1. Automated ingestion adds items to `ingestion_queue`
2. Human reviewers access queue via admin interface
3. Reviewers verify source credibility and relevance
4. Approved items move to main `incidents` table
5. Rejected items are marked and retained for audit

## Security Considerations

### API Access Control

- Ingestion endpoints require `admin` or `editor` role
- All ingestion operations are logged with user ID
- Failed authentication attempts are rate-limited

### Data Validation

- All URLs are validated before fetching
- RSS/XML parsing uses safe parsers (feedparser)
- HTML content extraction sanitizes inputs
- YouTube video IDs are validated against YouTube URL patterns

### Resource Limits

- Task timeouts: 30 minutes hard limit, 25 minutes soft limit
- Rate limiting on external API calls (respects robots.txt)
- Maximum content length limits prevent memory exhaustion
- Celery worker memory limits configured in docker-compose.yml

## References

- **Celery Documentation**: https://docs.celeryproject.org/
- **Celery Beat Schedules**: https://docs.celeryproject.org/en/stable/userguide/periodic-tasks.html
- **feedparser**: https://feedparser.readthedocs.io/
- **youtube-transcript-api**: https://github.com/jdepoix/youtube-transcript-api
- **YouTube RSS Feeds**: https://support.google.com/youtube/answer/6224202
