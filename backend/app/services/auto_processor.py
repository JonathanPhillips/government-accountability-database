"""Auto-processing service for ingestion queue items."""
from sqlalchemy.orm import Session
from typing import Dict, List, Tuple
from app.models.ingestion_queue import IngestionQueue
from app.models.base import IngestionStatusEnum


class AutoProcessor:
    """Intelligent auto-processor for ingestion queue items."""

    # High-confidence keywords for auto-approval
    GOVERNMENT_KEYWORDS = [
        'government', 'federal', 'agency', 'department', 'official',
        'ice', 'fbi', 'dhs', 'doj', 'cia', 'nsa', 'atf', 'dea',
        'police', 'law enforcement', 'sheriff', 'marshal',
        'surveillance', 'monitoring', 'tracking', 'spying',
        'misconduct', 'abuse', 'corruption', 'violation',
        'investigation', 'probe', 'lawsuit', 'court',
        'constitutional', 'rights', 'civil liberties', 'freedom',
        'trump', 'biden', 'congress', 'senate', 'house',
        'military', 'pentagon', 'defense', 'national security'
    ]

    # Keywords for auto-rejection
    REJECT_KEYWORDS = [
        'sports', 'football', 'basketball', 'tennis', 'cricket',
        'entertainment', 'celebrity', 'actor', 'actress',
        'fashion', 'style', 'beauty', 'cooking', 'recipe',
        'weather', 'forecast', 'temperature'
    ]

    # Trusted sources with high relevance
    TRUSTED_SPECIALIZED_SOURCES = {
        'eff.org': 0.9,  # 90% relevance rate
        'propublica.org': 0.8,  # 80% relevance rate
        'theintercept.com': 0.8  # 80% relevance rate
    }

    # General news sources (lower relevance)
    GENERAL_NEWS_SOURCES = {
        'bbci.co.uk': 0.2,  # 20% relevance rate
        'npr.org': 0.4  # 40% relevance rate
    }

    def __init__(self, db: Session):
        """Initialize auto-processor with database session."""
        self.db = db

    def calculate_keyword_score(self, text: str) -> int:
        """Calculate keyword relevance score for text."""
        if not text:
            return 0

        text_lower = text.lower()
        score = 0

        for keyword in self.GOVERNMENT_KEYWORDS:
            if keyword in text_lower:
                # Weight important keywords higher
                if keyword in ['ice', 'fbi', 'dhs', 'surveillance', 'corruption', 'misconduct']:
                    score += 2
                else:
                    score += 1

        return score

    def get_source_domain(self, url: str) -> str:
        """Extract domain from URL."""
        if not url:
            return ''

        # Simple domain extraction
        for domain in list(self.TRUSTED_SPECIALIZED_SOURCES.keys()) + list(self.GENERAL_NEWS_SOURCES.keys()):
            if domain in url:
                return domain

        return ''

    def is_high_confidence_approve(self, item: IngestionQueue) -> Tuple[bool, str]:
        """Determine if item should be auto-approved with high confidence."""
        if not item.extracted_data:
            return False, "No extracted data"

        title = item.extracted_data.get('title', '').lower()
        feed_url = item.extracted_data.get('feed_url', '')
        domain = self.get_source_domain(feed_url)

        # EFF articles about surveillance/government
        if domain == 'eff.org':
            keyword_score = self.calculate_keyword_score(title)
            if keyword_score >= 2:
                return True, f"EFF article with high keyword relevance (score: {keyword_score})"

        # ProPublica investigations
        if domain == 'propublica.org':
            if any(kw in title for kw in ['government', 'federal', 'investigation', 'officials', 'misconduct', 'abuse']):
                keyword_score = self.calculate_keyword_score(title)
                return True, f"ProPublica investigation (score: {keyword_score})"

        # The Intercept national security/civil liberties
        if domain == 'theintercept.com':
            if any(kw in title for kw in ['government', 'surveillance', 'military', 'intelligence', 'national security']):
                keyword_score = self.calculate_keyword_score(title)
                return True, f"The Intercept article on government/security (score: {keyword_score})"

        # High keyword score from any reputable source
        keyword_score = self.calculate_keyword_score(title)
        if keyword_score >= 4 and domain in self.TRUSTED_SPECIALIZED_SOURCES:
            return True, f"High keyword score from trusted source (score: {keyword_score})"

        return False, "Does not meet high confidence criteria"

    def is_auto_reject(self, item: IngestionQueue) -> Tuple[bool, str]:
        """Determine if item should be auto-rejected."""
        if not item.extracted_data:
            return False, "No extracted data"

        title = item.extracted_data.get('title', '').lower()
        feed_url = item.extracted_data.get('feed_url', '')
        domain = self.get_source_domain(feed_url)

        # Check for off-topic keywords
        for keyword in self.REJECT_KEYWORDS:
            if keyword in title:
                return True, f"Off-topic: contains '{keyword}'"

        # BBC non-US news
        if domain == 'bbci.co.uk':
            us_keywords = ['us', 'usa', 'america', 'american', 'trump', 'biden', 'washington', 'federal']
            if not any(kw in title for kw in us_keywords):
                if not any(kw in title for kw in ['government', 'police', 'surveillance']):
                    return True, "BBC article without US government connection"

        return False, "Not an auto-reject candidate"

    def process_item(self, item: IngestionQueue, dry_run: bool = False) -> Dict[str, any]:
        """
        Process a single item with auto-approval logic.

        Args:
            item: IngestionQueue item to process
            dry_run: If True, don't actually update the database

        Returns:
            dict with decision, confidence, reason, and keyword_score
        """
        # Calculate keyword score
        title = item.extracted_data.get('title', '') if item.extracted_data else ''
        keyword_score = self.calculate_keyword_score(title)

        # Check for high confidence auto-approval
        should_approve, approve_reason = self.is_high_confidence_approve(item)
        if should_approve:
            if not dry_run:
                item.status = IngestionStatusEnum.APPROVED
                item.auto_processed = True
                item.auto_confidence = 'HIGH'
                item.auto_reason = approve_reason
                item.keyword_score = keyword_score

            return {
                'decision': 'approved',
                'confidence': 'HIGH',
                'reason': approve_reason,
                'keyword_score': keyword_score
            }

        # Check for auto-rejection
        should_reject, reject_reason = self.is_auto_reject(item)
        if should_reject:
            if not dry_run:
                item.status = IngestionStatusEnum.REJECTED
                item.auto_processed = True
                item.auto_confidence = 'HIGH'
                item.auto_reason = reject_reason
                item.keyword_score = keyword_score

            return {
                'decision': 'rejected',
                'confidence': 'HIGH',
                'reason': reject_reason,
                'keyword_score': keyword_score
            }

        # Needs human review
        return {
            'decision': 'review_needed',
            'confidence': 'LOW',
            'reason': 'Requires human judgment',
            'keyword_score': keyword_score
        }

    def process_batch(
        self,
        limit: int = 100,
        dry_run: bool = False
    ) -> Dict[str, any]:
        """
        Process a batch of pending items.

        Args:
            limit: Maximum number of items to process
            dry_run: If True, simulate processing without updating database

        Returns:
            Statistics about processing results
        """
        # Get pending items not yet auto-processed
        items = self.db.query(IngestionQueue).filter(
            IngestionQueue.status == IngestionStatusEnum.PENDING,
            IngestionQueue.auto_processed == False
        ).limit(limit).all()

        results = {
            'total_processed': 0,
            'approved': 0,
            'rejected': 0,
            'review_needed': 0,
            'high_confidence': 0,
            'medium_confidence': 0,
            'low_confidence': 0,
            'items': []
        }

        for item in items:
            result = self.process_item(item, dry_run=dry_run)
            results['total_processed'] += 1

            if result['decision'] == 'approved':
                results['approved'] += 1
            elif result['decision'] == 'rejected':
                results['rejected'] += 1
            else:
                results['review_needed'] += 1

            if result['confidence'] == 'HIGH':
                results['high_confidence'] += 1
            elif result['confidence'] == 'MEDIUM':
                results['medium_confidence'] += 1
            else:
                results['low_confidence'] += 1

            # Include sample items in response
            if len(results['items']) < 10:
                results['items'].append({
                    'id': item.id,
                    'title': item.extracted_data.get('title', 'No title') if item.extracted_data else 'No title',
                    'decision': result['decision'],
                    'confidence': result['confidence'],
                    'reason': result['reason'],
                    'keyword_score': result['keyword_score']
                })

        if not dry_run:
            self.db.commit()

        return results

    def get_statistics(self) -> Dict[str, any]:
        """Get statistics about auto-processing results."""
        total = self.db.query(IngestionQueue).count()
        auto_processed = self.db.query(IngestionQueue).filter(
            IngestionQueue.auto_processed == True
        ).count()

        auto_approved = self.db.query(IngestionQueue).filter(
            IngestionQueue.auto_processed == True,
            IngestionQueue.status == IngestionStatusEnum.APPROVED
        ).count()

        auto_rejected = self.db.query(IngestionQueue).filter(
            IngestionQueue.auto_processed == True,
            IngestionQueue.status == IngestionStatusEnum.REJECTED
        ).count()

        pending = self.db.query(IngestionQueue).filter(
            IngestionQueue.status == IngestionStatusEnum.PENDING,
            IngestionQueue.auto_processed == False
        ).count()

        return {
            'total_items': total,
            'auto_processed': auto_processed,
            'auto_approved': auto_approved,
            'auto_rejected': auto_rejected,
            'pending_review': pending,
            'automation_rate': round((auto_processed / total * 100), 2) if total > 0 else 0
        }
