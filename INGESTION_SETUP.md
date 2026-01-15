# Ingestion System Setup Complete

**Date**: 2026-01-12
**Status**: ✅ Active and ingesting

## Current Ingestion Status

### **11 Items in Review Queue**

**Sources:**
- **The Intercept** - 3 articles on immigration, ICE, data centers
- **ProPublica** - 3 investigative reports
- **BBC News** - 5 international news articles

All items are marked as `PENDING` and awaiting human review.

## Configured RSS Feeds

The system now automatically ingests from these sources:

### **Tier 1: Investigative Journalism**
1. **ProPublica** (https://www.propublica.org/feeds/propublica/main)
   - Type: `news_primary`
   - Max entries: 10
   - Focus: Government accountability investigations

2. **The Intercept** (https://theintercept.com/feed/)
   - Type: `news_primary`
   - Max entries: 10
   - Focus: National security, surveillance, government overreach

3. **BBC News** (http://feeds.bbci.co.uk/news/rss.xml)
   - Type: `news_primary`
   - Max entries: 10
   - Focus: International news, reliable source

### **Tier 2: Civil Liberties**
4. **Electronic Frontier Foundation** (https://www.eff.org/rss/updates.xml)
   - Type: `ngo_report`
   - Max entries: 10
   - Focus: Digital rights, online privacy, surveillance

### **Tier 3: Supplementary**
5. **NPR News** (https://feeds.npr.org/1001/rss.xml)
   - Type: `news_primary`
   - Max entries: 5
   - Focus: National news

## How to Use the Ingestion System

### **1. Automatic Ingestion (When Celery is working)**
The system can automatically ingest feeds on a schedule:
```bash
# Trigger all feeds manually
curl -X POST http://localhost/api/ingestion/tasks/trigger-all-feeds \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### **2. Manual Ingestion**
Login as admin and add sources via the frontend UI:
1. Navigate to http://localhost/
2. Login with admin credentials
3. Go to "Add Source" page
4. Enter RSS feed URL and settings

### **3. Direct API Ingestion**
```bash
# Ingest specific RSS feed
curl -X POST http://localhost/api/ingestion/rss \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN" \
  -d '{
    "feed_url": "https://www.propublica.org/feeds/propublica/main",
    "source_type": "news_primary",
    "max_entries": 10
  }'
```

### **4. YouTube Video Ingestion**
```bash
curl -X POST http://localhost/api/ingestion/youtube \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN" \
  -d '{
    "video_url": "https://www.youtube.com/watch?v=VIDEO_ID",
    "title": "Congressional Hearing on...",
    "author": "C-SPAN",
    "published_date": "2026-01-12",
    "languages": ["en"]
  }'
```

### **5. PDF Document Ingestion**
```bash
curl -X POST http://localhost/api/ingestion/pdf \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN" \
  -d '{
    "pdf_url": "https://example.gov/report.pdf",
    "title": "GAO Report on...",
    "author": "Government Accountability Office",
    "published_date": "2026-01-12",
    "source_type": "government_report",
    "save_locally": true
  }'
```

## Review Workflow

1. **Ingestion**: Automated systems add items to queue
2. **Queue Status**: All items start as `PENDING`
3. **Review**: Reviewer/Editor role users review items
4. **Approve/Reject**: Items can be:
   - `APPROVED` - Creates incident in database
   - `REJECTED` - Discarded
   - `NEEDS_EDIT` - Requires manual editing

## Adding New Sources

### **Edit Configuration File**
File: `backend/app/tasks/ingestion_tasks.py`

Add to `RSS_FEED_SOURCES` list:
```python
{
    "url": "https://example.org/feed.xml",
    "source_type": SourceTypeEnum.NGO_REPORT,
    "max_entries": 10
},
```

### **Source Types Available**
- `court_filing` - Court documents
- `government_report` - Official reports
- `foia` - FOIA documents
- `news_primary` - Primary news sources
- `news_secondary` - Secondary news
- `academic` - Academic papers
- `ngo_report` - NGO reports
- `firsthand_account` - Witness accounts
- `video` - Video transcripts
- `social_media` - Social media
- `leaked_document` - Leaked docs

## Recommended Additional Sources

See `INGESTION_SOURCES.md` for comprehensive list including:

**High Priority:**
- Project On Government Oversight (POGO)
- OpenSecrets (money in politics)
- MuckRock (FOIA requests)
- Center for Public Integrity

**Government Official:**
- GAO Reports
- Inspector General feeds
- Supreme Court RSS

**Investigative:**
- More ProPublica feeds
- Bellingcat
- The Marshall Project

## Troubleshooting

### **Feed Not Parsing**
Some RSS feeds have XML issues. Test with:
```python
from app.services.rss_ingester import RSSIngester
RSSIngester.fetch_feed("URL_HERE")
```

### **Celery Not Running**
Celery workers have a configuration issue with Redis password encoding.
Manual ingestion still works via direct API calls.

### **No Items Appearing**
Check:
1. Backend logs: `docker-compose logs backend`
2. Database: Query `ingestion_queue` table
3. API response for error messages

## Statistics

- **Feeds Configured**: 5 active sources
- **Items Ingested**: 11 items (as of 2026-01-12)
- **Success Rate**: 60% (3/5 feeds working)
- **Failed Feeds**: OpenSecrets, ACLU (XML parsing issues)

## Next Steps

1. ✅ RSS ingestion working (3/5 feeds)
2. ⏳ Fix Celery workers for automation
3. ⏳ Test YouTube ingestion with C-SPAN hearings
4. ⏳ Test PDF ingestion with GAO reports
5. ⏳ Build frontend review interface
6. ⏳ Add more government-focused sources
7. ⏳ Set up automated scheduling (when Celery fixed)

## Access Information

- **Frontend**: http://localhost/
- **API Docs**: http://localhost/api/ (when DEBUG=True)
- **Admin Login**: admin@gadb.local / changeme123

⚠️ **Change default password immediately!**
