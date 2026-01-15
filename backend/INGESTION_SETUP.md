# Ingestion System Setup and Testing Guide

This guide walks through setting up and testing the automated ingestion system for the Government Accountability Database.

## Prerequisites

- Docker and Docker Compose installed and running
- All containers started with `docker-compose up -d`
- Backend, PostgreSQL, Redis, Celery Worker, and Celery Beat containers running

## System Architecture

The ingestion system consists of several components:

```
┌─────────────────┐
│   Celery Beat   │ - Schedules periodic ingestion tasks
│   (Scheduler)   │
└────────┬────────┘
         │ Triggers tasks at scheduled times
         ▼
┌─────────────────┐
│ Celery Worker   │ - Executes ingestion tasks
│ (Task Executor) │ - Fetches RSS feeds and YouTube videos
└────────┬────────┘
         │ Writes to database
         ▼
┌─────────────────┐
│ Ingestion Queue │ - Stores items awaiting human review
│  (Database)     │ - Status: PENDING, APPROVED, REJECTED
└─────────────────┘
```

## Verifying Container Status

```bash
# Check all containers are running
docker-compose ps

# Expected output:
# NAME                 STATUS
# gadb-backend         Up X minutes (healthy)
# gadb-celery-worker   Up X minutes (healthy)
# gadb-celery-beat     Up X minutes (healthy)
# gadb-frontend        Up X minutes
# gadb-postgres        Up X minutes (healthy)
# gadb-redis           Up X minutes (healthy)

# Check Celery worker logs
docker-compose logs celery-worker --tail=20

# Should see: "celery@<hostname> ready."

# Check Celery beat logs
docker-compose logs celery-beat --tail=20

# Should see scheduled tasks being registered
```

## Testing Manual Ingestion

### Test RSS Feed Ingestion

```bash
# Enter the backend container
docker exec -it gadb-backend python3

# In Python shell:
from app.tasks.ingestion_tasks import ingest_rss_feed, RSS_FEED_SOURCES
from app.database import SessionLocal

# Manually trigger ProPublica RSS ingestion
result = ingest_rss_feed.delay(
    feed_url="https://www.propublica.org/feeds/propublica/main",
    source_type="NEWS_PRIMARY",
    max_entries=5
)

# Check task status
print(f"Task ID: {result.id}")
print(f"Task State: {result.state}")
print(f"Task Result: {result.result}")

# Exit Python
exit()
```

### Test YouTube Channel Ingestion

```bash
# Enter the backend container
docker exec -it gadb-backend python3

# In Python shell:
from app.tasks.ingestion_tasks import ingest_youtube_channel

# Manually trigger ProPublica YouTube channel ingestion
result = ingest_youtube_channel.delay(
    channel_id="UCe02lGcO-ahAURWuxAJnjdA",
    name="ProPublica",
    source_type="VIDEO",
    max_videos=3
)

# Check task status
print(f"Task ID: {result.id}")
print(f"Task State: {result.state}")

# Wait for task to complete (may take 10-30 seconds)
result.wait(timeout=60)
print(f"Task Result: {result.result}")

# Exit Python
exit()
```

### Verify Ingestion Queue

```bash
# Connect to PostgreSQL
docker exec -it gadb-postgres psql -U gadb -d gadb

# Query ingestion queue
SELECT
    id,
    source_type,
    status,
    created_at,
    substring(source_url, 1, 60) as url_preview
FROM ingestion_queue
ORDER BY created_at DESC
LIMIT 10;

# Count items by source type
SELECT source_type, status, COUNT(*) as count
FROM ingestion_queue
GROUP BY source_type, status;

# Exit PostgreSQL
\q
```

## Testing Automated Scheduled Ingestion

### View Configured Schedules

```bash
# Check Celery Beat schedule
docker exec -it gadb-celery-beat celery -A app.celery_app inspect scheduled

# Should show:
# - ingest-all-feeds (every 2 hours)
# - ingest-all-youtube-channels (every 4 hours)
# - ingest-all-sources-daily (daily at 3 AM)
# - cleanup-old-queue-items (Sundays at 2 AM)
```

### Manually Trigger Scheduled Tasks

```bash
# Trigger all RSS feeds ingestion
docker exec -it gadb-backend python3 -c "
from app.tasks.ingestion_tasks import ingest_all_feeds
result = ingest_all_feeds.delay()
print(f'Triggered RSS ingestion: {result.id}')
"

# Trigger all YouTube channels ingestion
docker exec -it gadb-backend python3 -c "
from app.tasks.ingestion_tasks import ingest_all_youtube_channels
result = ingest_all_youtube_channels.delay()
print(f'Triggered YouTube ingestion: {result.id}')
"

# Trigger comprehensive ingestion from all sources
docker exec -it gadb-backend python3 -c "
from app.tasks.ingestion_tasks import ingest_all_sources
result = ingest_all_sources.delay()
print(f'Triggered all sources ingestion: {result.id}')
"
```

### Monitor Task Execution in Real-Time

```bash
# Watch Celery worker logs in real-time
docker-compose logs -f celery-worker

# Watch for:
# [INFO] Task app.tasks.ingestion_tasks.ingest_rss_feed[<task-id>] received
# [INFO] Successfully ingested X entries from <feed-url>
# [INFO] Task app.tasks.ingestion_tasks.ingest_rss_feed[<task-id>] succeeded

# Press Ctrl+C to stop watching
```

## Verifying Ingestion Results

### Check Task Results in Database

```bash
# Count ingested items
docker exec -it gadb-postgres psql -U gadb -d gadb -c "
SELECT COUNT(*) as total_items, status
FROM ingestion_queue
GROUP BY status;
"

# View recent ingestion items
docker exec -it gadb-postgres psql -U gadb -d gadb -c "
SELECT
    id,
    source_type,
    status,
    created_at,
    extracted_data->>'title' as title
FROM ingestion_queue
ORDER BY created_at DESC
LIMIT 20;
"
```

### Check RSS Feed Ingestion

```bash
docker exec -it gadb-postgres psql -U gadb -d gadb -c "
SELECT
    COUNT(*) as rss_items,
    source_type,
    status
FROM ingestion_queue
WHERE source_type IN ('NEWS_PRIMARY', 'NEWS_SECONDARY', 'CIVIL_LIBERTIES')
GROUP BY source_type, status;
"
```

### Check YouTube Video Ingestion

```bash
docker exec -it gadb-postgres psql -U gadb -d gadb -c "
SELECT
    COUNT(*) as video_count,
    status,
    extracted_data->>'platform' as platform
FROM ingestion_queue
WHERE source_type = 'VIDEO'
GROUP BY status, platform;
"

# View YouTube video details
docker exec -it gadb-postgres psql -U gadb -d gadb -c "
SELECT
    id,
    created_at,
    extracted_data->>'title' as title,
    extracted_data->>'author' as channel,
    extracted_data->>'video_id' as video_id,
    LENGTH(raw_content) as transcript_length
FROM ingestion_queue
WHERE source_type = 'VIDEO'
ORDER BY created_at DESC
LIMIT 5;
"
```

## Troubleshooting

### Celery Worker Not Processing Tasks

```bash
# Check worker is running and connected
docker-compose logs celery-worker | grep "ready"

# Should see: "celery@<hostname> ready."

# Check Redis connection
docker exec -it gadb-redis redis-cli ping
# Should return: PONG

# Check task queue in Redis
docker exec -it gadb-redis redis-cli LLEN celery
# Shows number of pending tasks (should be 0 if all processed)

# Restart Celery worker
docker-compose restart celery-worker
```

### Celery Beat Not Scheduling Tasks

```bash
# Check beat is running
docker-compose logs celery-beat | grep "Scheduler"

# Should see schedule entries being registered

# Check beat schedule database
docker exec -it gadb-backend ls -la /app/celerybeat-schedule

# Restart Celery beat
docker-compose restart celery-beat
```

### RSS Feed Fails to Ingest

```bash
# Check worker logs for errors
docker-compose logs celery-worker | grep -i error

# Test feed URL manually
curl -I https://www.propublica.org/feeds/propublica/main

# Should return: HTTP/2 200

# Validate feed XML
curl -s https://www.propublica.org/feeds/propublica/main | head -50
# Should show valid XML structure
```

### YouTube Transcript Not Available

```bash
# Check worker logs
docker-compose logs celery-worker | grep -i transcript

# Note: Not all videos have transcripts
# This is expected behavior - videos without transcripts will skip transcript extraction
```

### Ingestion Queue Growing Too Large

```bash
# Check current queue size
docker exec -it gadb-postgres psql -U gadb -d gadb -c "
SELECT status, COUNT(*) as count
FROM ingestion_queue
GROUP BY status;
"

# Manually clean up old processed items
docker exec -it gadb-backend python3 -c "
from app.tasks.ingestion_tasks import cleanup_old_queue_items
result = cleanup_old_queue_items.delay(days=30)
print(f'Triggered cleanup: {result.id}')
"
```

## Production Deployment Checklist

Before deploying to production:

- [ ] **Verify all containers start successfully**
  ```bash
  docker-compose ps
  # All should show "healthy" or "Up"
  ```

- [ ] **Test manual RSS ingestion**
  ```bash
  # Should add items to ingestion_queue with status=PENDING
  ```

- [ ] **Test manual YouTube ingestion**
  ```bash
  # Should add videos with transcripts to ingestion_queue
  ```

- [ ] **Verify scheduled tasks are registered**
  ```bash
  docker exec -it gadb-celery-beat celery -A app.celery_app inspect scheduled
  ```

- [ ] **Check Celery worker can process tasks**
  ```bash
  # Trigger a test task and verify it completes
  ```

- [ ] **Verify database connectivity**
  ```bash
  docker exec -it gadb-postgres psql -U gadb -d gadb -c "SELECT COUNT(*) FROM ingestion_queue;"
  ```

- [ ] **Test Redis connection**
  ```bash
  docker exec -it gadb-redis redis-cli ping
  ```

- [ ] **Review and adjust ingestion schedules**
  - Edit `backend/app/celerybeat_schedule.py` as needed
  - Restart Celery beat after changes

- [ ] **Configure source lists**
  - Edit `backend/app/tasks/ingestion_tasks.py`
  - Update RSS_FEED_SOURCES and YOUTUBE_CHANNEL_SOURCES
  - Restart Celery worker after changes

- [ ] **Set up monitoring and alerting**
  - Monitor Celery worker health
  - Alert on ingestion failures
  - Track queue growth

## Testing Checklist

Use this checklist to verify the ingestion system is working:

### Initial Setup
- [ ] All Docker containers running and healthy
- [ ] Backend API responding at http://localhost:8000/health
- [ ] Redis responding to PING
- [ ] PostgreSQL accepting connections
- [ ] Celery worker shows "ready" in logs
- [ ] Celery beat shows scheduled tasks in logs

### Manual Ingestion Tests
- [ ] RSS feed ingestion adds items to database
- [ ] YouTube channel ingestion adds videos to database
- [ ] Ingestion queue items have status=PENDING
- [ ] Extracted data contains expected fields (title, author, etc.)
- [ ] Raw content is populated (article text or transcript)

### Automated Ingestion Tests
- [ ] Scheduled tasks appear in `celery inspect scheduled`
- [ ] Can manually trigger `ingest_all_feeds` task
- [ ] Can manually trigger `ingest_all_youtube_channels` task
- [ ] Can manually trigger `ingest_all_sources` task
- [ ] Tasks execute without errors in worker logs

### Data Verification
- [ ] Ingestion queue has items from RSS feeds
- [ ] Ingestion queue has items from YouTube videos
- [ ] Items have correct source_type (NEWS_PRIMARY, VIDEO, etc.)
- [ ] Timestamps are accurate (created_at, updated_at)
- [ ] No duplicate entries (same source_url)

### Error Handling
- [ ] Invalid feed URLs log errors but don't crash worker
- [ ] Missing YouTube transcripts are handled gracefully
- [ ] Failed tasks retry with exponential backoff
- [ ] After max retries, tasks are marked as failed

### Cleanup
- [ ] Can manually trigger cleanup_old_queue_items
- [ ] Cleanup only removes old APPROVED/REJECTED items
- [ ] PENDING items are never deleted by cleanup
- [ ] Cleanup respects the days parameter

## Performance Expectations

### RSS Feed Ingestion
- **Processing Time**: 5-30 seconds per feed
- **Items Per Feed**: Typically 5-15 items
- **Expected Success Rate**: >95%
- **Common Failures**: Network timeouts, malformed XML

### YouTube Video Ingestion
- **Processing Time**: 10-60 seconds per channel
- **Videos Per Channel**: 1-10 new videos typically
- **Transcript Availability**: ~70% of videos
- **Expected Success Rate**: >90%

### Celery Worker Performance
- **Task Throughput**: 1-5 tasks per second
- **Memory Usage**: ~100-200MB per worker
- **CPU Usage**: <30% average, bursts to 80% during ingestion

### Database Performance
- **Ingestion Queue Growth**: ~50-200 items per day with default schedule
- **Query Performance**: <100ms for list queries, <10ms for by-ID
- **Cleanup Performance**: ~1000 items/second deletion rate

## Monitoring Metrics

### Key Metrics to Track

1. **Task Success Rate**
   ```sql
   SELECT
     COUNT(CASE WHEN status = 'PENDING' THEN 1 END) as successful,
     COUNT(*) as total,
     ROUND(100.0 * COUNT(CASE WHEN status = 'PENDING' THEN 1 END) / COUNT(*), 2) as success_rate_percent
   FROM ingestion_queue
   WHERE created_at > NOW() - INTERVAL '24 hours';
   ```

2. **Average Ingestion Lag**
   ```sql
   SELECT
     source_type,
     AVG(EXTRACT(EPOCH FROM (created_at - (extracted_data->>'published_date')::timestamp))) / 3600 as avg_lag_hours
   FROM ingestion_queue
   WHERE created_at > NOW() - INTERVAL '7 days'
   GROUP BY source_type;
   ```

3. **Queue Size by Status**
   ```sql
   SELECT status, COUNT(*) as count
   FROM ingestion_queue
   GROUP BY status;
   ```

4. **Celery Task Queue Length**
   ```bash
   docker exec -it gadb-redis redis-cli LLEN celery
   ```

## Common Issues and Solutions

### Issue: "email-validator is not installed"

**Symptom**: Celery worker crashes with ImportError about email-validator

**Solution**:
```bash
# Rebuild Celery containers
docker-compose build celery-worker celery-beat
docker-compose up -d celery-worker celery-beat
```

### Issue: Tasks not being picked up by worker

**Symptom**: Tasks stay in "PENDING" state indefinitely

**Solution**:
```bash
# Check worker is connected
docker-compose logs celery-worker | grep "Connected to redis"

# Restart worker
docker-compose restart celery-worker

# Check Redis has tasks
docker exec -it gadb-redis redis-cli LLEN celery
```

### Issue: Scheduled tasks not running

**Symptom**: No automatic ingestion happening

**Solution**:
```bash
# Check beat is running
docker-compose ps celery-beat

# Check beat logs for schedule
docker-compose logs celery-beat | grep "Scheduler"

# Restart beat
docker-compose restart celery-beat
```

### Issue: Duplicate ingestion items

**Symptom**: Same articles/videos appear multiple times

**Solution**:
```sql
-- Find duplicates
SELECT source_url, COUNT(*) as count
FROM ingestion_queue
GROUP BY source_url
HAVING COUNT(*) > 1;

-- Delete duplicates (keep oldest)
DELETE FROM ingestion_queue a
USING ingestion_queue b
WHERE a.id > b.id
AND a.source_url = b.source_url;
```

## Next Steps

After verifying the ingestion system works:

1. **Configure Production Schedules**
   - Adjust crontab expressions in `celerybeat_schedule.py`
   - Consider server timezone vs UTC

2. **Add More Sources**
   - Research additional RSS feeds and YouTube channels
   - Add to configuration in `ingestion_tasks.py`

3. **Set Up Monitoring**
   - Configure Sentry for error tracking
   - Set up Prometheus/Grafana for metrics
   - Create alerts for ingestion failures

4. **Optimize Performance**
   - Increase Celery workers if needed (`docker-compose up -d --scale celery-worker=3`)
   - Adjust `max_entries` and `max_videos` based on review capacity
   - Implement result caching if needed

5. **Implement Admin Interface**
   - Create API endpoints for managing sources
   - Build UI for viewing/approving ingestion queue
   - Add bulk approve/reject functionality

## Support

For issues or questions:
- Check logs: `docker-compose logs celery-worker` and `docker-compose logs celery-beat`
- Review source code: `backend/app/tasks/ingestion_tasks.py`
- Consult documentation: `INGESTION_SOURCES.md`
- Report bugs: GitHub Issues
