"""Seed database with initial data for GADB."""
import sys
import os
from datetime import date, timedelta

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import SessionLocal, engine, Base
from app.models import (
    Category, Actor, Target, LegalFramework, Pattern, Incident,
    IncidentActor, IncidentTarget, IncidentLegalFramework, IncidentPattern,
    Source
)
from app.models.base import (
    ActorTypeEnum, ActorRoleEnum, SeverityEnum, VerificationStatusEnum,
    GeographicScopeEnum, LegalFrameworkTypeEnum, SourceTypeEnum, ReliabilityEnum,
    ViolationTypeEnum
)


def create_categories(db):
    """Create all incident categories."""
    print("Creating categories...")

    # Check if categories already exist
    if db.query(Category).count() > 0:
        print("  Categories already exist, skipping...")
        return

    categories = [
        {
            "id": "court_order_defiance",
            "name": "Court Order Defiance",
            "description": "Instances where government actors defy or ignore court orders"
        },
        {
            "id": "due_process_violations",
            "name": "Due Process Violations",
            "description": "Violations of constitutional due process rights"
        },
        {
            "id": "unlawful_detention",
            "name": "Unlawful Detention",
            "description": "Detention of individuals without legal basis or beyond legal limits"
        },
        {
            "id": "selective_enforcement",
            "name": "Selective Enforcement",
            "description": "Discriminatory or targeted enforcement of laws"
        },
        {
            "id": "surveillance_abuse",
            "name": "Surveillance Abuse",
            "description": "Unlawful or excessive surveillance of individuals or groups"
        },
        {
            "id": "force_excessive",
            "name": "Excessive Force",
            "description": "Use of force beyond what is necessary or reasonable"
        },
        {
            "id": "transparency_violations",
            "name": "Transparency Violations",
            "description": "Failure to provide required transparency or access to information"
        },
        {
            "id": "whistleblower_retaliation",
            "name": "Whistleblower Retaliation",
            "description": "Retaliation against individuals who report misconduct"
        },
        {
            "id": "policy_reversal",
            "name": "Policy Reversal",
            "description": "Abrupt changes in policy without proper procedure or notice"
        },
        {
            "id": "resource_misuse",
            "name": "Resource Misuse",
            "description": "Misuse or waste of public resources"
        }
    ]

    for cat_data in categories:
        category = Category(**cat_data)
        db.add(category)

    db.commit()
    print(f"Created {len(categories)} categories")


def create_actors(db):
    """Create government actors and agencies."""
    print("Creating actors...")

    # Check if actors already exist
    if db.query(Actor).count() > 0:
        print("  Actors already exist, skipping...")
        return

    actors = [
        # Federal agencies
        {"id": "dhs", "name": "Department of Homeland Security", "actor_type": ActorTypeEnum.AGENCY, "active": True},
        {"id": "ice", "name": "Immigration and Customs Enforcement", "actor_type": ActorTypeEnum.AGENCY, "parent_actor_id": "dhs", "active": True},
        {"id": "cbp", "name": "Customs and Border Protection", "actor_type": ActorTypeEnum.AGENCY, "parent_actor_id": "dhs", "active": True},
        {"id": "doj", "name": "Department of Justice", "actor_type": ActorTypeEnum.AGENCY, "active": True},
        {"id": "fbi", "name": "Federal Bureau of Investigation", "actor_type": ActorTypeEnum.AGENCY, "parent_actor_id": "doj", "active": True},
        {"id": "dod", "name": "Department of Defense", "actor_type": ActorTypeEnum.AGENCY, "active": True},
        {"id": "epa", "name": "Environmental Protection Agency", "actor_type": ActorTypeEnum.AGENCY, "active": True},
        {"id": "hhs", "name": "Department of Health and Human Services", "actor_type": ActorTypeEnum.AGENCY, "active": True},
        {"id": "ed", "name": "Department of Education", "actor_type": ActorTypeEnum.AGENCY, "active": True},
        {"id": "state_dept", "name": "Department of State", "actor_type": ActorTypeEnum.AGENCY, "active": True},

        # State/local
        {"id": "nypd", "name": "New York Police Department", "actor_type": ActorTypeEnum.AGENCY, "active": True},
        {"id": "lapd", "name": "Los Angeles Police Department", "actor_type": ActorTypeEnum.AGENCY, "active": True},
    ]

    for actor_data in actors:
        actor = Actor(**actor_data)
        db.add(actor)

    db.commit()
    print(f"Created {len(actors)} actors")


def create_targets(db):
    """Create target populations."""
    print("Creating targets...")

    # Check if targets already exist
    if db.query(Target).count() > 0:
        print("  Targets already exist, skipping...")
        return

    targets = [
        {"id": "asylum_seekers", "name": "Asylum Seekers", "description": "Individuals seeking asylum protection"},
        {"id": "immigrants_undocumented", "name": "Undocumented Immigrants", "description": "People living in the country without legal status"},
        {"id": "refugees", "name": "Refugees", "description": "Individuals granted refugee status"},
        {"id": "journalists", "name": "Journalists", "description": "Members of the press and media"},
        {"id": "protesters", "name": "Protesters", "description": "Individuals participating in protests or demonstrations"},
        {"id": "religious_minorities", "name": "Religious Minorities", "description": "Members of minority religious groups"},
        {"id": "lgbtq", "name": "LGBTQ+ Community", "description": "Lesbian, gay, bisexual, transgender, and queer individuals"},
        {"id": "racial_minorities", "name": "Racial Minorities", "description": "Members of racial minority groups"},
        {"id": "whistleblowers", "name": "Whistleblowers", "description": "Individuals who report government misconduct"},
        {"id": "environmental_activists", "name": "Environmental Activists", "description": "Individuals advocating for environmental protection"},
    ]

    for target_data in targets:
        target = Target(**target_data)
        db.add(target)

    db.commit()
    print(f"Created {len(targets)} targets")


def create_legal_frameworks(db):
    """Create legal frameworks."""
    print("Creating legal frameworks...")

    # Check if legal frameworks already exist
    if db.query(LegalFramework).count() > 0:
        print("  Legal frameworks already exist, skipping...")
        return

    frameworks = [
        {
            "id": "constitution_1st",
            "name": "First Amendment",
            "description": "Freedom of speech, religion, press, assembly",
            "framework_type": LegalFrameworkTypeEnum.CONSTITUTIONAL,
            "citation": "U.S. Constitution, Amendment I"
        },
        {
            "id": "constitution_4th",
            "name": "Fourth Amendment",
            "description": "Protection against unreasonable searches and seizures",
            "framework_type": LegalFrameworkTypeEnum.CONSTITUTIONAL,
            "citation": "U.S. Constitution, Amendment IV"
        },
        {
            "id": "constitution_5th",
            "name": "Fifth Amendment",
            "description": "Due process, self-incrimination, double jeopardy",
            "framework_type": LegalFrameworkTypeEnum.CONSTITUTIONAL,
            "citation": "U.S. Constitution, Amendment V"
        },
        {
            "id": "constitution_14th",
            "name": "Fourteenth Amendment",
            "description": "Equal protection and due process",
            "framework_type": LegalFrameworkTypeEnum.CONSTITUTIONAL,
            "citation": "U.S. Constitution, Amendment XIV"
        },
        {
            "id": "apa",
            "name": "Administrative Procedure Act",
            "description": "Governs federal agency rulemaking and adjudication",
            "framework_type": LegalFrameworkTypeEnum.STATUTORY,
            "citation": "5 U.S.C. §§ 551-559"
        },
        {
            "id": "foia",
            "name": "Freedom of Information Act",
            "description": "Public access to government records",
            "framework_type": LegalFrameworkTypeEnum.STATUTORY,
            "citation": "5 U.S.C. § 552"
        },
        {
            "id": "ina",
            "name": "Immigration and Nationality Act",
            "description": "Federal immigration law",
            "framework_type": LegalFrameworkTypeEnum.STATUTORY,
            "citation": "8 U.S.C. § 1101 et seq."
        },
        {
            "id": "refugee_act",
            "name": "Refugee Act of 1980",
            "description": "Framework for refugee admissions and asylum",
            "framework_type": LegalFrameworkTypeEnum.STATUTORY,
            "citation": "8 U.S.C. § 1157"
        },
    ]

    for framework_data in frameworks:
        framework = LegalFramework(**framework_data)
        db.add(framework)

    db.commit()
    print(f"Created {len(frameworks)} legal frameworks")


def create_patterns(db):
    """Create systematic patterns."""
    print("Creating patterns...")

    # Check if patterns already exist
    if db.query(Pattern).count() > 0:
        print("  Patterns already exist, skipping...")
        return

    patterns = [
        {
            "id": "court_defiance_pattern",
            "name": "Systematic Court Order Defiance",
            "description": "Pattern of ignoring or defying court orders across multiple jurisdictions"
        },
        {
            "id": "detention_quota",
            "name": "Detention Quota System",
            "description": "Systematic detention driven by quotas rather than legal necessity"
        },
        {
            "id": "family_separation",
            "name": "Family Separation Policy",
            "description": "Systematic separation of families as deterrent or punishment"
        },
        {
            "id": "due_process_denial",
            "name": "Due Process Denial Pattern",
            "description": "Systematic denial of due process rights"
        },
        {
            "id": "transparency_obstruction",
            "name": "Transparency Obstruction",
            "description": "Pattern of obstructing transparency and oversight"
        },
    ]

    for pattern_data in patterns:
        pattern = Pattern(**pattern_data)
        db.add(pattern)

    db.commit()
    print(f"Created {len(patterns)} patterns")


def create_incidents(db):
    """Create sample incidents with relationships."""
    print("Creating sample incidents...")

    # Check if incidents already exist
    if db.query(Incident).count() > 0:
        print("  Sample incidents already exist, skipping...")
        return

    # Incident 1: ICE Court Order Defiance
    incident1 = Incident(
        id="incident_001",
        title="ICE Defies Court Order to Release Detainees",
        date_occurred=date(2025, 1, 15),
        summary="ICE agents refused to comply with federal court order mandating release of asylum seekers",
        detailed_description="Federal judge issued order requiring ICE to release asylum seekers who had been detained beyond legal limits. ICE officials acknowledged receipt of the order but continued to hold detainees, citing 'operational constraints' and 'security concerns' not specified in their formal response.",
        category_id="court_order_defiance",
        severity=SeverityEnum.HIGH,
        verification_status=VerificationStatusEnum.DOCUMENTED,
        geographic_scope=GeographicScopeEnum.FEDERAL,
        location_state="Texas",
        location_city="El Paso"
    )
    db.add(incident1)
    db.commit()

    # Add actors
    db.add(IncidentActor(incident_id=incident1.id, actor_id="ice", role=ActorRoleEnum.PERPETRATOR))
    db.add(IncidentActor(incident_id=incident1.id, actor_id="dhs", role=ActorRoleEnum.COMPLICIT))

    # Add targets
    db.add(IncidentTarget(incident_id=incident1.id, target_id="asylum_seekers"))

    # Add legal frameworks
    db.add(IncidentLegalFramework(incident_id=incident1.id, legal_framework_id="constitution_5th", violation_type=ViolationTypeEnum.DOCUMENTED))
    db.add(IncidentLegalFramework(incident_id=incident1.id, legal_framework_id="ina", violation_type=ViolationTypeEnum.DOCUMENTED))

    # Add patterns
    db.add(IncidentPattern(incident_id=incident1.id, pattern_id="court_defiance_pattern"))

    # Add source
    source1 = Source(
        incident_id=incident1.id,
        title="Federal Court Order Defied by ICE",
        source_type=SourceTypeEnum.COURT_FILING,
        url="https://example.com/court-order-ice-defiance",
        publication_date=date(2025, 1, 16),
        reliability=ReliabilityEnum.PRIMARY,
        author="U.S. District Court"
    )
    db.add(source1)

    db.commit()

    # Incident 2: Unlawful Surveillance
    incident2 = Incident(
        id="incident_002",
        title="FBI Conducts Warrantless Surveillance of Journalists",
        date_occurred=date(2025, 1, 20),
        summary="FBI conducted electronic surveillance of journalists without obtaining required warrants",
        detailed_description="Documents revealed FBI surveillance program targeting journalists covering national security topics. Surveillance included phone records, emails, and location tracking conducted without judicial oversight.",
        category_id="surveillance_abuse",
        severity=SeverityEnum.CRITICAL,
        verification_status=VerificationStatusEnum.DOCUMENTED,
        geographic_scope=GeographicScopeEnum.FEDERAL
    )
    db.add(incident2)
    db.commit()

    db.add(IncidentActor(incident_id=incident2.id, actor_id="fbi", role=ActorRoleEnum.PERPETRATOR))
    db.add(IncidentActor(incident_id=incident2.id, actor_id="doj", role=ActorRoleEnum.COMPLICIT))
    db.add(IncidentTarget(incident_id=incident2.id, target_id="journalists"))
    db.add(IncidentLegalFramework(incident_id=incident2.id, legal_framework_id="constitution_1st", violation_type=ViolationTypeEnum.DOCUMENTED))
    db.add(IncidentLegalFramework(incident_id=incident2.id, legal_framework_id="constitution_4th", violation_type=ViolationTypeEnum.DOCUMENTED))

    source2 = Source(
        incident_id=incident2.id,
        title="FBI Surveillance Program Revealed",
        source_type=SourceTypeEnum.NEWS_PRIMARY,
        url="https://example.com/fbi-surveillance",
        publication_date=date(2025, 1, 22),
        reliability=ReliabilityEnum.PRIMARY,
        author="Major Newspaper"
    )
    db.add(source2)

    db.commit()

    # Incident 3: Excessive Force
    incident3 = Incident(
        id="incident_003",
        title="Police Use Excessive Force Against Protesters",
        date_occurred=date(2025, 2, 1),
        summary="Police deployed tear gas and rubber bullets against peaceful protesters",
        detailed_description="During peaceful demonstration, police escalated response without provocation, deploying chemical agents and less-lethal weapons. Multiple protesters hospitalized with serious injuries.",
        category_id="force_excessive",
        severity=SeverityEnum.HIGH,
        verification_status=VerificationStatusEnum.DOCUMENTED,
        geographic_scope=GeographicScopeEnum.STATE,
        location_state="California",
        location_city="Los Angeles"
    )
    db.add(incident3)
    db.commit()

    db.add(IncidentActor(incident_id=incident3.id, actor_id="lapd", role=ActorRoleEnum.PERPETRATOR))
    db.add(IncidentTarget(incident_id=incident3.id, target_id="protesters"))
    db.add(IncidentLegalFramework(incident_id=incident3.id, legal_framework_id="constitution_1st", violation_type=ViolationTypeEnum.DOCUMENTED))
    db.add(IncidentLegalFramework(incident_id=incident3.id, legal_framework_id="constitution_14th", violation_type=ViolationTypeEnum.DOCUMENTED))

    source3 = Source(
        incident_id=incident3.id,
        title="Video Evidence of Police Excessive Force",
        source_type=SourceTypeEnum.VIDEO,
        url="https://example.com/protest-video",
        publication_date=date(2025, 2, 2),
        reliability=ReliabilityEnum.PRIMARY
    )
    db.add(source3)

    db.commit()

    # Incident 4: Whistleblower Retaliation
    incident4 = Incident(
        id="incident_004",
        title="EPA Retaliates Against Climate Scientist Whistleblower",
        date_occurred=date(2025, 2, 10),
        summary="EPA demoted and reassigned scientist who reported data manipulation",
        detailed_description="Senior EPA scientist reported manipulation of climate research data. Following internal complaint, scientist was demoted, reassigned to non-research role, and subjected to hostile work environment.",
        category_id="whistleblower_retaliation",
        severity=SeverityEnum.MEDIUM,
        verification_status=VerificationStatusEnum.DOCUMENTED,
        geographic_scope=GeographicScopeEnum.FEDERAL
    )
    db.add(incident4)
    db.commit()

    db.add(IncidentActor(incident_id=incident4.id, actor_id="epa", role=ActorRoleEnum.PERPETRATOR))
    db.add(IncidentTarget(incident_id=incident4.id, target_id="whistleblowers"))
    db.add(IncidentTarget(incident_id=incident4.id, target_id="environmental_activists"))
    db.add(IncidentPattern(incident_id=incident4.id, pattern_id="transparency_obstruction"))

    source4 = Source(
        incident_id=incident4.id,
        title="EPA Scientist Files Whistleblower Complaint",
        source_type=SourceTypeEnum.GOVERNMENT_REPORT,
        url="https://example.com/epa-whistleblower",
        publication_date=date(2025, 2, 12),
        reliability=ReliabilityEnum.PRIMARY,
        author="Office of Special Counsel"
    )
    db.add(source4)

    db.commit()

    # Incident 5: Due Process Violations
    incident5 = Incident(
        id="incident_005",
        title="ICE Conducts Mass Arrests Without Warrants",
        date_occurred=date(2025, 2, 15),
        summary="ICE conducted raids targeting immigrant communities without judicial warrants",
        detailed_description="ICE agents conducted coordinated raids across multiple cities, arresting individuals without judicial warrants. Many detainees held without access to counsel or timely hearings.",
        category_id="due_process_violations",
        severity=SeverityEnum.HIGH,
        verification_status=VerificationStatusEnum.DOCUMENTED,
        geographic_scope=GeographicScopeEnum.FEDERAL
    )
    db.add(incident5)
    db.commit()

    db.add(IncidentActor(incident_id=incident5.id, actor_id="ice", role=ActorRoleEnum.PERPETRATOR))
    db.add(IncidentTarget(incident_id=incident5.id, target_id="immigrants_undocumented"))
    db.add(IncidentLegalFramework(incident_id=incident5.id, legal_framework_id="constitution_4th", violation_type=ViolationTypeEnum.DOCUMENTED))
    db.add(IncidentLegalFramework(incident_id=incident5.id, legal_framework_id="constitution_5th", violation_type=ViolationTypeEnum.DOCUMENTED))
    db.add(IncidentPattern(incident_id=incident5.id, pattern_id="due_process_denial"))

    source5 = Source(
        incident_id=incident5.id,
        title="ACLU Documents ICE Raid Pattern",
        source_type=SourceTypeEnum.NGO_REPORT,
        url="https://example.com/aclu-ice-raids",
        publication_date=date(2025, 2, 17),
        reliability=ReliabilityEnum.PRIMARY,
        author="ACLU"
    )
    db.add(source5)

    db.commit()

    print("Created 5 detailed sample incidents with sources and relationships")


def main():
    """Main seed data function."""
    print("Starting database seed...")
    print("=" * 60)

    # Create database session
    db = SessionLocal()

    try:
        # Create all data
        create_categories(db)
        create_actors(db)
        create_targets(db)
        create_legal_frameworks(db)
        create_patterns(db)
        create_incidents(db)

        print("=" * 60)
        print("Database seed completed successfully!")
        print("\nSummary:")
        print(f"  Categories: {db.query(Category).count()}")
        print(f"  Actors: {db.query(Actor).count()}")
        print(f"  Targets: {db.query(Target).count()}")
        print(f"  Legal Frameworks: {db.query(LegalFramework).count()}")
        print(f"  Patterns: {db.query(Pattern).count()}")
        print(f"  Incidents: {db.query(Incident).count()}")
        print(f"  Sources: {db.query(Source).count()}")

    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
