"""Base model and common enums."""
import enum
from datetime import datetime
from sqlalchemy import Column, DateTime
from sqlalchemy.dialects.postgresql import UUID
import uuid


class SeverityEnum(str, enum.Enum):
    """Severity levels for incidents."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class VerificationStatusEnum(str, enum.Enum):
    """Verification status for incidents."""
    UNVERIFIED = "unverified"
    PENDING_REVIEW = "pending_review"
    DISPUTED = "disputed"
    DOCUMENTED = "documented"
    ADJUDICATED = "adjudicated"


class GeographicScopeEnum(str, enum.Enum):
    """Geographic scope of incidents."""
    LOCAL = "local"
    STATE = "state"
    FEDERAL = "federal"
    INTERNATIONAL = "international"


class ActorTypeEnum(str, enum.Enum):
    """Types of actors."""
    AGENCY = "agency"
    OFFICIAL = "official"
    CONTRACTOR = "contractor"
    ENTITY = "entity"
    FOREIGN_GOVERNMENT = "foreign_government"


class ActorRoleEnum(str, enum.Enum):
    """Roles of actors in incidents."""
    PERPETRATOR = "perpetrator"
    COMPLICIT = "complicit"
    RESISTOR = "resistor"
    WHISTLEBLOWER = "whistleblower"


class PersonRoleEnum(str, enum.Enum):
    """Roles of persons in incidents."""
    ORDERED = "ordered"
    EXECUTED = "executed"
    RESISTED = "resisted"
    EXPOSED = "exposed"


class LegalFrameworkTypeEnum(str, enum.Enum):
    """Types of legal frameworks."""
    CONSTITUTIONAL = "constitutional"
    STATUTORY = "statutory"
    TREATY = "treaty"
    COURT_ORDER = "court_order"
    REGULATION = "regulation"


class ViolationTypeEnum(str, enum.Enum):
    """Types of legal violations."""
    ALLEGED = "alleged"
    DOCUMENTED = "documented"
    ADJUDICATED = "adjudicated"


class SourceTypeEnum(str, enum.Enum):
    """Types of sources."""
    COURT_FILING = "court_filing"
    GOVERNMENT_REPORT = "government_report"
    FOIA = "foia"
    NEWS_PRIMARY = "news_primary"
    NEWS_SECONDARY = "news_secondary"
    ACADEMIC = "academic"
    NGO_REPORT = "ngo_report"
    FIRSTHAND_ACCOUNT = "firsthand_account"
    VIDEO = "video"
    SOCIAL_MEDIA = "social_media"
    LEAKED_DOCUMENT = "leaked_document"


class ReliabilityEnum(str, enum.Enum):
    """Reliability levels for sources."""
    PRIMARY = "primary"
    SECONDARY = "secondary"
    TERTIARY = "tertiary"


class RelationshipTypeEnum(str, enum.Enum):
    """Types of relationships between incidents."""
    PRECEDED_BY = "preceded_by"
    FOLLOWED_BY = "followed_by"
    RELATED = "related"
    ESCALATION_OF = "escalation_of"
    RESPONSE_TO = "response_to"


class IngestionStatusEnum(str, enum.Enum):
    """Status of ingestion queue items."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_EDIT = "needs_edit"


class UserRoleEnum(str, enum.Enum):
    """User roles for authorization."""
    ADMIN = "admin"           # Full system access
    EDITOR = "editor"         # Can create/edit incidents, manage queue
    REVIEWER = "reviewer"     # Can review queue items, view all data
    VIEWER = "viewer"         # Read-only access


class TimestampMixin:
    """Mixin for created_at and updated_at timestamps."""
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


def generate_uuid():
    """Generate UUID for primary keys."""
    return str(uuid.uuid4())
