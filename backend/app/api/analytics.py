"""Analytics API endpoints."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import Dict, List

from app.database import get_db
from app.models.incident import Incident
from app.models.base import SeverityEnum, VerificationStatusEnum, GeographicScopeEnum

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/overview")
def get_analytics_overview(db: Session = Depends(get_db)) -> Dict:
    """
    Get overview analytics for the dashboard.

    Returns statistics on incidents including:
    - Total counts
    - Breakdown by severity
    - Breakdown by verification status
    - Breakdown by geographic scope
    - Recent trends
    """
    # Total incidents
    total_incidents = db.query(Incident).count()

    # Incidents by severity
    severity_counts = (
        db.query(Incident.severity, func.count(Incident.id))
        .group_by(Incident.severity)
        .all()
    )
    by_severity = {str(severity): count for severity, count in severity_counts}

    # Incidents by verification status
    verification_counts = (
        db.query(Incident.verification_status, func.count(Incident.id))
        .group_by(Incident.verification_status)
        .all()
    )
    by_verification = {str(status): count for status, count in verification_counts}

    # Incidents by geographic scope
    scope_counts = (
        db.query(Incident.geographic_scope, func.count(Incident.id))
        .group_by(Incident.geographic_scope)
        .all()
    )
    by_scope = {str(scope): count for scope, count in scope_counts}

    # Recent activity (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_count = (
        db.query(Incident)
        .filter(Incident.created_at >= thirty_days_ago)
        .count()
    )

    # Top states by incident count
    state_counts = (
        db.query(Incident.location_state, func.count(Incident.id))
        .filter(Incident.location_state.isnot(None))
        .group_by(Incident.location_state)
        .order_by(func.count(Incident.id).desc())
        .limit(10)
        .all()
    )
    top_states = [{"state": state, "count": count} for state, count in state_counts]

    return {
        "total_incidents": total_incidents,
        "by_severity": by_severity,
        "by_verification": by_verification,
        "by_geographic_scope": by_scope,
        "recent_30_days": recent_count,
        "top_states": top_states,
        "last_updated": datetime.utcnow().isoformat()
    }


@router.get("/timeline")
def get_timeline_data(
    days: int = 365,
    db: Session = Depends(get_db)
) -> Dict:
    """
    Get incident timeline data for charts.

    Returns incidents grouped by month for the specified number of days.
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days)

    # Get incidents by month
    monthly_counts = (
        db.query(
            func.date_trunc('month', Incident.date_occurred).label('month'),
            func.count(Incident.id).label('count')
        )
        .filter(Incident.date_occurred >= cutoff_date)
        .group_by('month')
        .order_by('month')
        .all()
    )

    timeline = [
        {
            "month": month.strftime("%Y-%m") if month else "Unknown",
            "count": count
        }
        for month, count in monthly_counts
    ]

    return {
        "timeline": timeline,
        "days": days
    }


@router.get("/categories")
def get_category_statistics(db: Session = Depends(get_db)) -> Dict:
    """Get incident statistics by category."""
    from app.models.category import Category

    # Get category counts
    category_stats = (
        db.query(
            Category.name,
            func.count(Incident.id).label('count')
        )
        .join(Incident, Category.id == Incident.category_id)
        .group_by(Category.id, Category.name)
        .order_by(func.count(Incident.id).desc())
        .all()
    )

    return {
        "categories": [
            {"name": name, "count": count}
            for name, count in category_stats
        ]
    }


@router.get("/verification-trends")
def get_verification_trends(db: Session = Depends(get_db)) -> Dict:
    """Get verification status trends over time."""
    # Get verification status counts by month for the last year
    one_year_ago = datetime.utcnow() - timedelta(days=365)

    trends = (
        db.query(
            func.date_trunc('month', Incident.created_at).label('month'),
            Incident.verification_status,
            func.count(Incident.id).label('count')
        )
        .filter(Incident.created_at >= one_year_ago)
        .group_by('month', Incident.verification_status)
        .order_by('month')
        .all()
    )

    # Organize by month
    monthly_data = {}
    for month, status, count in trends:
        month_key = month.strftime("%Y-%m") if month else "Unknown"
        if month_key not in monthly_data:
            monthly_data[month_key] = {}
        monthly_data[month_key][str(status)] = count

    return {
        "trends": [
            {"month": month, "data": data}
            for month, data in sorted(monthly_data.items())
        ]
    }
