"""Incident service for business logic."""
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, or_, and_
from typing import List, Optional, Tuple
from app.models import (
    Incident, Source, IncidentActor, IncidentPerson, IncidentTarget,
    IncidentLegalFramework, IncidentPattern, Actor, Person, Target,
    LegalFramework, Pattern
)
from app.models.base import ActorRoleEnum, PersonRoleEnum, ViolationTypeEnum
from app.schemas.incident import IncidentCreate, IncidentUpdate, IncidentFilters


class IncidentService:
    """Service for incident operations."""

    @staticmethod
    def create(db: Session, incident: IncidentCreate, created_by: str = "system") -> Incident:
        """Create a new incident with optional relationships."""
        # Create incident without relationships
        incident_data = incident.model_dump(exclude={'actor_ids', 'person_ids', 'target_ids', 'legal_framework_ids', 'pattern_ids'})
        db_incident = Incident(**incident_data, created_by=created_by)
        db.add(db_incident)
        db.flush()  # Get the ID without committing

        # Add relationships if provided
        if incident.actor_ids:
            for actor_id in incident.actor_ids:
                db.add(IncidentActor(
                    incident_id=db_incident.id,
                    actor_id=actor_id,
                    role=ActorRoleEnum.PERPETRATOR
                ))

        if incident.target_ids:
            for target_id in incident.target_ids:
                db.add(IncidentTarget(incident_id=db_incident.id, target_id=target_id))

        if incident.legal_framework_ids:
            for lf_id in incident.legal_framework_ids:
                db.add(IncidentLegalFramework(
                    incident_id=db_incident.id,
                    legal_framework_id=lf_id,
                    violation_type=ViolationTypeEnum.ALLEGED
                ))

        if incident.pattern_ids:
            for pattern_id in incident.pattern_ids:
                db.add(IncidentPattern(incident_id=db_incident.id, pattern_id=pattern_id))

        db.commit()
        db.refresh(db_incident)
        return db_incident

    @staticmethod
    def get_by_id(db: Session, incident_id: str, load_relationships: bool = False) -> Optional[Incident]:
        """Get incident by ID, optionally with relationships loaded."""
        query = db.query(Incident)
        if load_relationships:
            query = query.options(
                joinedload(Incident.sources),
                joinedload(Incident.actors),
                joinedload(Incident.persons),
                joinedload(Incident.targets),
                joinedload(Incident.legal_frameworks),
                joinedload(Incident.patterns)
            )
        return query.filter(Incident.id == incident_id).first()

    @staticmethod
    def get_list(db: Session, filters: IncidentFilters) -> Tuple[List[Incident], int]:
        """Get incidents with filtering and pagination."""
        query = db.query(Incident)

        # Apply filters
        if filters.category_id:
            query = query.filter(Incident.category_id == filters.category_id)

        if filters.severity:
            query = query.filter(Incident.severity == filters.severity)

        if filters.verification_status:
            query = query.filter(Incident.verification_status == filters.verification_status)

        if filters.geographic_scope:
            query = query.filter(Incident.geographic_scope == filters.geographic_scope)

        if filters.location_state:
            query = query.filter(Incident.location_state == filters.location_state)

        if filters.date_from:
            query = query.filter(Incident.date_occurred >= filters.date_from)

        if filters.date_to:
            query = query.filter(Incident.date_occurred <= filters.date_to)

        # Filter by actor
        if filters.actor_id:
            query = query.join(IncidentActor).filter(IncidentActor.actor_id == filters.actor_id)

        # Filter by person
        if filters.person_id:
            query = query.join(IncidentPerson).filter(IncidentPerson.person_id == filters.person_id)

        # Filter by target
        if filters.target_id:
            query = query.join(IncidentTarget).filter(IncidentTarget.target_id == filters.target_id)

        # Filter by pattern
        if filters.pattern_id:
            query = query.join(IncidentPattern).filter(IncidentPattern.pattern_id == filters.pattern_id)

        # Filter by legal framework
        if filters.legal_framework_id:
            query = query.join(IncidentLegalFramework).filter(
                IncidentLegalFramework.legal_framework_id == filters.legal_framework_id
            )

        # Search across title and summary
        if filters.search:
            search_term = f"%{filters.search}%"
            query = query.filter(or_(
                Incident.title.ilike(search_term),
                Incident.summary.ilike(search_term),
                Incident.detailed_description.ilike(search_term)
            ))

        # Get total count before pagination
        total = query.count()

        # Apply pagination and ordering
        incidents = query.order_by(Incident.date_occurred.desc()).offset(filters.skip).limit(filters.limit).all()

        return incidents, total

    @staticmethod
    def update(db: Session, incident_id: str, incident_update: IncidentUpdate) -> Optional[Incident]:
        """Update an incident."""
        db_incident = db.query(Incident).filter(Incident.id == incident_id).first()
        if not db_incident:
            return None

        update_data = incident_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_incident, key, value)

        db.commit()
        db.refresh(db_incident)
        return db_incident

    @staticmethod
    def delete(db: Session, incident_id: str) -> bool:
        """Delete an incident (cascade deletes sources and relationships)."""
        db_incident = db.query(Incident).filter(Incident.id == incident_id).first()
        if not db_incident:
            return False

        db.delete(db_incident)
        db.commit()
        return True

    @staticmethod
    def add_actor(db: Session, incident_id: str, actor_id: str, role: ActorRoleEnum) -> Optional[IncidentActor]:
        """Add an actor to an incident."""
        # Check if relationship already exists
        existing = db.query(IncidentActor).filter(
            IncidentActor.incident_id == incident_id,
            IncidentActor.actor_id == actor_id
        ).first()

        if existing:
            return existing

        incident_actor = IncidentActor(incident_id=incident_id, actor_id=actor_id, role=role)
        db.add(incident_actor)
        db.commit()
        db.refresh(incident_actor)
        return incident_actor

    @staticmethod
    def add_target(db: Session, incident_id: str, target_id: str) -> Optional[IncidentTarget]:
        """Add a target to an incident."""
        existing = db.query(IncidentTarget).filter(
            IncidentTarget.incident_id == incident_id,
            IncidentTarget.target_id == target_id
        ).first()

        if existing:
            return existing

        incident_target = IncidentTarget(incident_id=incident_id, target_id=target_id)
        db.add(incident_target)
        db.commit()
        db.refresh(incident_target)
        return incident_target

    @staticmethod
    def add_pattern(db: Session, incident_id: str, pattern_id: str) -> Optional[IncidentPattern]:
        """Add a pattern to an incident."""
        existing = db.query(IncidentPattern).filter(
            IncidentPattern.incident_id == incident_id,
            IncidentPattern.pattern_id == pattern_id
        ).first()

        if existing:
            return existing

        incident_pattern = IncidentPattern(incident_id=incident_id, pattern_id=pattern_id)
        db.add(incident_pattern)
        db.commit()
        db.refresh(incident_pattern)
        return incident_pattern

    @staticmethod
    def add_legal_framework(db: Session, incident_id: str, legal_framework_id: str, violation_type: ViolationTypeEnum) -> Optional[IncidentLegalFramework]:
        """Add a legal framework to an incident."""
        existing = db.query(IncidentLegalFramework).filter(
            IncidentLegalFramework.incident_id == incident_id,
            IncidentLegalFramework.legal_framework_id == legal_framework_id
        ).first()

        if existing:
            return existing

        incident_lf = IncidentLegalFramework(
            incident_id=incident_id,
            legal_framework_id=legal_framework_id,
            violation_type=violation_type
        )
        db.add(incident_lf)
        db.commit()
        db.refresh(incident_lf)
        return incident_lf

    @staticmethod
    def get_source_count(db: Session, incident_id: str) -> int:
        """Get count of sources for an incident."""
        return db.query(func.count(Source.id)).filter(Source.incident_id == incident_id).scalar()

    @staticmethod
    def create_from_queue_item(db: Session, queue_item, created_by: str = "system") -> List[Incident]:
        """
        Extract and create incidents from an approved ingestion queue item using LLM.

        Note: One article can contain multiple incidents, so this returns a list.

        Args:
            db: Database session
            queue_item: IngestionQueue item with status=APPROVED and raw_content
            created_by: User who created the incident

        Returns:
            List of created Incident objects (can be empty if no incidents extracted)
        """
        from app.models import IngestionQueue, Category, Actor
        from app.models.base import (
            IngestionStatusEnum, SeverityEnum, GeographicScopeEnum,
            ActorRoleEnum, ReliabilityEnum
        )
        from app.schemas.incident import IncidentCreate
        from app.services.extraction_service import ExtractionService
        from datetime import datetime
        import re

        # Only process approved items
        if queue_item.status != IngestionStatusEnum.APPROVED:
            return []

        # Use LLM to extract incident data
        extractor = ExtractionService()
        extracted_incidents = extractor.extract_from_queue_item(queue_item)

        if not extracted_incidents:
            print(f"No incidents extracted from queue item {queue_item.id}")
            return []

        created_incidents = []

        # Get default category
        default_category = db.query(Category).filter(Category.name == "Uncategorized").first()
        if not default_category:
            default_category = Category(name="Uncategorized", description="Items without specific category")
            db.add(default_category)
            db.flush()

        # Parse article metadata
        extracted_meta = queue_item.extracted_data or {}
        article_title = extracted_meta.get('title', queue_item.source_url)
        author = extracted_meta.get('author')
        published_date_str = extracted_meta.get('published_date')

        published_date = None
        if published_date_str:
            try:
                published_date = datetime.fromisoformat(published_date_str.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                published_date = None

        # Process each extracted incident
        for incident_data in extracted_incidents:
            try:
                # Parse incident date
                incident_date_str = incident_data.get('date')
                incident_date = None
                if incident_date_str:
                    try:
                        # Try to parse various date formats
                        for fmt in ['%Y-%m-%d', '%Y/%m/%d', '%m/%d/%Y', '%B %d, %Y']:
                            try:
                                incident_date = datetime.strptime(incident_date_str, fmt).date()
                                break
                            except ValueError:
                                continue
                    except:
                        pass

                if not incident_date:
                    # Use article publication date or today
                    incident_date = published_date.date() if published_date else datetime.utcnow().date()

                # Parse location to extract state
                location = incident_data.get('location', '')
                state = None
                # Simple state extraction (City, ST format)
                state_match = re.search(r',\s*([A-Z]{2})\b', location)
                if state_match:
                    state = state_match.group(1)

                # Determine geographic scope
                if state:
                    geo_scope = GeographicScopeEnum.STATE
                elif 'federal' in location.lower() or 'ICE' in str(incident_data.get('actors', [])):
                    geo_scope = GeographicScopeEnum.FEDERAL
                else:
                    geo_scope = GeographicScopeEnum.LOCAL

                # Check for duplicates (same title and similar date)
                existing = db.query(Incident).filter(
                    Incident.title == incident_data.get('title')
                ).first()

                if existing:
                    print(f"Skipping duplicate incident: {incident_data.get('title')}")
                    continue

                # Create incident
                incident_create = IncidentCreate(
                    title=incident_data.get('title', 'Untitled Incident'),
                    summary=incident_data.get('what_happened', '')[:1000],  # Limit summary length
                    detailed_description=incident_data.get('what_happened', ''),
                    date_occurred=incident_date,
                    category_id=default_category.id,
                    severity=SeverityEnum.MEDIUM,
                    location_state=state,
                    location_city=location.split(',')[0].strip() if ',' in location else None,
                    geographic_scope=geo_scope
                )

                incident = IncidentService.create(db, incident_create, created_by=created_by)

                # Add actors (perpetrators)
                actors_list = incident_data.get('actors', [])
                for actor_str in actors_list:
                    if not actor_str:
                        continue

                    # Try to parse "Name, Organization" format
                    parts = actor_str.split(',', 1)
                    actor_name = parts[0].strip()
                    org_info = parts[1].strip() if len(parts) > 1 else None

                    # Check if actor exists
                    actor = db.query(Actor).filter(Actor.name == actor_name).first()
                    if not actor:
                        # Determine actor type based on name/organization
                        from app.models.base import ActorTypeEnum
                        if any(keyword in actor_name.lower() for keyword in ['agent', 'officer', 'official', 'director']):
                            actor_type = ActorTypeEnum.OFFICIAL
                        else:
                            actor_type = ActorTypeEnum.AGENCY

                        actor = Actor(
                            name=actor_name,
                            actor_type=actor_type,
                            description=org_info if org_info else None
                        )
                        db.add(actor)
                        db.flush()

                    # Link actor to incident
                    IncidentService.add_actor(db, incident.id, actor.id, ActorRoleEnum.PERPETRATOR)

                # Add legal frameworks (laws violated)
                # TODO: Create LegalFramework records and link them

                # Create source record
                source = Source(
                    incident_id=incident.id,
                    title=article_title,
                    url=queue_item.source_url,
                    source_type=queue_item.source_type,
                    author=author,
                    publication_date=published_date.date() if published_date else None,
                    reliability=ReliabilityEnum.SECONDARY,
                    excerpt=incident_data.get('what_happened', '')[:500]
                )
                db.add(source)

                created_incidents.append(incident)

            except Exception as e:
                print(f"Error creating incident from extracted data: {str(e)}")
                print(f"Incident data: {incident_data}")
                continue

        # Mark queue item as converted (link to first incident if any)
        if created_incidents:
            queue_item.created_incident_id = created_incidents[0].id

        db.commit()

        for incident in created_incidents:
            db.refresh(incident)

        return created_incidents

    @staticmethod
    def convert_approved_queue_items(db: Session, limit: int = 100, created_by: str = "system") -> dict:
        """
        Convert multiple approved queue items to incidents.

        Args:
            db: Database session
            limit: Maximum number of items to convert
            created_by: User who triggered the conversion

        Returns:
            Dictionary with conversion statistics
        """
        from app.models import IngestionQueue
        from app.models.base import IngestionStatusEnum

        # Get approved items that haven't been converted yet
        approved_items = db.query(IngestionQueue).filter(
            IngestionQueue.status == IngestionStatusEnum.APPROVED,
            IngestionQueue.created_incident_id == None
        ).limit(limit).all()

        results = {
            'total_attempted': len(approved_items),
            'successful': 0,
            'failed': 0,
            'incident_ids': []
        }

        for item in approved_items:
            try:
                incident = IncidentService.create_from_queue_item(db, item, created_by)
                if incident:
                    results['successful'] += 1
                    results['incident_ids'].append(incident.id)
                else:
                    results['failed'] += 1
            except Exception as e:
                results['failed'] += 1
                print(f"Failed to convert queue item {item.id}: {str(e)}")

        return results
