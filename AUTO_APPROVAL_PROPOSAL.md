# Auto-Approval System Proposal

## Problem Statement

Current situation: **4,905 items** in queue, 100% requiring manual review.
Reality: ~60% could be auto-approved with high confidence, ~30% auto-rejected.

## Auto-Approval Tiers

### Tier 1: High Confidence Auto-Approve (Estimated 40%)

**Criteria:** Source + Keywords

#### EFF Articles (Almost Always Relevant)
```
IF source = "eff.org"
AND contains ANY["government", "surveillance", "police", "ICE", "FBI", "DHS", "privacy", "rights", "law enforcement"]
THEN auto_approve WITH confidence=HIGH
```

Examples:
- ✅ "ICE Is Going on a Surveillance Shopping Spree"
- ✅ "Baton Rouge Acquires a Straight-Up Military Surveillance Drone"
- ✅ "Report: ICE Using Palantir Tool That Feeds On Medicaid Data"

#### ProPublica Investigations
```
IF source = "propublica.org"
AND contains ANY["investigation", "government", "federal", "agency", "officials", "misconduct", "abuse"]
THEN auto_approve WITH confidence=HIGH
```

Examples:
- ✅ "We Found More Than 40 Cases of Immigration Agents Using Banned Chokeholds"
- ✅ "Trump Administration's Plan to Remake Public Education"
- ✅ "FBI Raid on WaPo Reporter's Home Was Based on Sham Pretext"

#### The Intercept (National Security)
```
IF source = "theintercept.com"
AND contains ANY["government", "surveillance", "military", "intelligence", "national security", "Trump", "Biden"]
THEN auto_approve WITH confidence=HIGH
```

### Tier 2: Medium Confidence Auto-Approve (Estimated 20%)

**Criteria:** Multiple keyword hits + reputable source

```
IF source IN ["propublica.org", "theintercept.com", "npr.org"]
AND keyword_score >= 3  # Multiple relevant keywords
THEN auto_approve WITH confidence=MEDIUM, flag=NEEDS_REVIEW
```

**Keyword Scoring:**
- government, federal, agency, department: +1 each
- police, ICE, FBI, DHS, DOJ, military: +2 each
- surveillance, abuse, misconduct, corruption, violation: +2 each
- constitutional, rights, civil liberties: +2 each
- investigation, probe, lawsuit, court: +1 each

### Tier 3: Auto-Reject (Estimated 30%)

**Criteria:** General news from broad feeds

#### BBC General News
```
IF source = "bbci.co.uk"
AND NOT contains ANY["US", "USA", "America", "government", "Trump", "Biden", "federal", "police"]
THEN auto_reject WITH reason="International general news"
```

Examples:
- ❌ "Djokovic registers 100th Australian Open win"
- ❌ "China's birth rate hits record low"
- ❌ "Man seriously injured in Sydney's third shark attack"

#### Off-Topic Content
```
IF contains ANY["sports", "entertainment", "celebrity", "fashion", "recipe"]
AND NOT contains ["government", "federal", "investigation"]
THEN auto_reject WITH reason="Off-topic"
```

### Tier 4: Requires Human Review (Estimated 10%)

**Edge Cases:**
- Healthcare/education stories (might involve government programs)
- Consumer protection (might involve regulatory agencies)
- Environmental stories (might involve federal policy)
- International news about US government
- Duplicate detection failures

```
IF confidence < MEDIUM
OR duplicate_score > 0.8
OR category = AMBIGUOUS
THEN flag_for_review WITH reason
```

## Implementation Strategy

### Phase 1: Conservative Auto-Approval (Week 1)

**Goal:** Process 60% of queue automatically with high accuracy

1. **Deploy Tier 1 only** - High confidence auto-approvals
   - EFF + keywords (estimated 500 items)
   - ProPublica investigations (estimated 1,500 items)
   - Expected accuracy: >95%

2. **Auto-reject obvious mismatches**
   - BBC international news without US connection
   - Sports, entertainment (estimated 1,000 items)
   - Expected accuracy: >98%

3. **Human review remainder** (~2,000 items)

### Phase 2: ML-Enhanced Filtering (Week 2)

1. **Train classifier** on Phase 1 human decisions
2. **Implement Tier 2** with ML confidence scoring
3. **Add duplicate detection**
4. **Reduce human review queue** to <500 items

### Phase 3: Continuous Learning (Ongoing)

1. **Monitor approval/rejection rates**
2. **Adjust thresholds** based on accuracy
3. **Add new keyword patterns** from human reviews
4. **Expand to new sources** as confidence grows

## Expected Results

### Before Auto-Approval
- Queue: 4,905 items
- Human review needed: 100% (4,905 items)
- Estimated time: 408 hours @ 5 min/item

### After Phase 1 (Conservative)
- Auto-approved: ~2,000 items (40%)
- Auto-rejected: ~1,500 items (30%)
- Human review needed: ~1,400 items (30%)
- **Time saved: ~290 hours (71%)**

### After Phase 2 (ML-Enhanced)
- Auto-approved: ~3,500 items (71%)
- Auto-rejected: ~1,000 items (20%)
- Human review needed: ~400 items (8%)
- **Time saved: ~375 hours (92%)**

## Quality Assurance

### Audit Process

1. **Random sampling** - Review 5% of auto-approvals weekly
2. **False positive tracking** - Monitor irrelevant items in database
3. **False negative tracking** - Spot-check auto-rejections monthly
4. **Accuracy targets:**
   - Auto-approve: >95% accuracy
   - Auto-reject: >98% accuracy
   - If below target: Adjust thresholds or revert to manual

### Rollback Plan

If auto-approval accuracy drops below 90%:
1. Pause auto-approval system
2. Review all auto-approved items from past week
3. Adjust criteria and re-test
4. Resume with tighter thresholds

## Technical Implementation

### Database Schema Addition

```sql
-- Add auto-processing fields to IngestionQueue
ALTER TABLE ingestion_queue ADD COLUMN auto_processed BOOLEAN DEFAULT FALSE;
ALTER TABLE ingestion_queue ADD COLUMN auto_confidence VARCHAR(20); -- HIGH, MEDIUM, LOW
ALTER TABLE ingestion_queue ADD COLUMN auto_reason TEXT;
ALTER TABLE ingestion_queue ADD COLUMN keyword_score INTEGER;
```

### Auto-Processor Service

```python
class AutoProcessor:
    def __init__(self, db: Session):
        self.db = db
        self.high_confidence_keywords = [
            'surveillance', 'ICE', 'FBI', 'DHS', 'police',
            'government', 'federal', 'misconduct', 'abuse'
        ]
        self.reject_keywords = ['sports', 'entertainment', 'celebrity']

    def process_item(self, item: IngestionQueue) -> str:
        """Returns: 'approved', 'rejected', or 'review_needed'"""

        # Tier 1: High confidence auto-approve
        if self._is_high_confidence_approve(item):
            item.status = 'approved'
            item.auto_processed = True
            item.auto_confidence = 'HIGH'
            return 'approved'

        # Tier 3: Auto-reject
        if self._is_auto_reject(item):
            item.status = 'rejected'
            item.auto_processed = True
            item.auto_reason = 'Off-topic or general news'
            return 'rejected'

        # Default: Human review
        return 'review_needed'

    def _is_high_confidence_approve(self, item: IngestionQueue) -> bool:
        title = item.extracted_data.get('title', '').lower()
        source = item.extracted_data.get('feed_url', '')

        # EFF articles about surveillance/government
        if 'eff.org' in source:
            if any(kw in title for kw in self.high_confidence_keywords):
                return True

        # ProPublica investigations
        if 'propublica.org' in source:
            if any(kw in title for kw in ['government', 'federal', 'investigation', 'officials']):
                return True

        return False

    def _is_auto_reject(self, item: IngestionQueue) -> bool:
        title = item.extracted_data.get('title', '').lower()
        source = item.extracted_data.get('feed_url', '')

        # BBC non-US news
        if 'bbci.co.uk' in source:
            if not any(kw in title for kw in ['us', 'usa', 'america', 'trump', 'biden']):
                return True

        # Off-topic content
        if any(kw in title for kw in self.reject_keywords):
            return True

        return False
```

### Celery Task for Batch Processing

```python
@celery_app.task
def auto_process_queue():
    """Process pending items in batches."""
    db = next(get_db())
    processor = AutoProcessor(db)

    # Get pending items
    items = db.query(IngestionQueue).filter(
        IngestionQueue.status == 'pending',
        IngestionQueue.auto_processed == False
    ).limit(100).all()

    results = {'approved': 0, 'rejected': 0, 'review_needed': 0}

    for item in items:
        result = processor.process_item(item)
        results[result] += 1

    db.commit()
    return results
```

## Next Steps

1. **Review this proposal** - Does the logic make sense?
2. **Test on sample** - Run on 100 items, validate accuracy
3. **Implement Phase 1** - Deploy conservative auto-processing
4. **Monitor and adjust** - Track accuracy, tune thresholds
5. **Expand to Phase 2** - Add ML when comfortable

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Auto-approve irrelevant content | Medium | Regular audits, accuracy monitoring |
| Auto-reject relevant content | High | Manual review of rejections monthly |
| Keyword gaming by bad sources | Low | Only applies to trusted sources |
| Classification drift over time | Medium | Continuous monitoring, quarterly reviews |

## Success Metrics

- **Accuracy**: >95% for auto-approvals, >98% for auto-rejections
- **Time savings**: >70% reduction in manual review time
- **Queue size**: Reduce to <500 items requiring human review
- **Processing speed**: Auto-process 2,000+ items in <1 hour
- **User satisfaction**: Reviewers spend time on edge cases, not obvious decisions
