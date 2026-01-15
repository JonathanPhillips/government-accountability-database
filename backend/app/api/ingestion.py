"""Ingestion API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional, Dict
from celery.result import AsyncResult

from app.database import get_db
from app.models import IngestionQueue
from app.models.base import IngestionStatusEnum, UserRoleEnum
from app.models.user import User
from app.schemas.ingestion import (
    IngestionQueueResponse,
    IngestionQueueUpdate,
    RSSFeedIngestRequest,
    RSSFeedIngestResponse,
    YouTubeIngestRequest,
    YouTubeIngestResponse,
    PDFIngestRequest,
    PDFIngestResponse,
)
from app.schemas.base import PaginatedResponse
from app.services.rss_ingester import RSSIngester
from app.services.youtube_ingester import YouTubeIngester
from app.services.pdf_processor import PDFProcessor
from app.tasks.ingestion_tasks import ingest_all_feeds, ingest_rss_feed as ingest_rss_task
from app.utils.deps import require_role

router = APIRouter()


@router.get("/", response_model=PaginatedResponse[IngestionQueueResponse])
def list_queue(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[IngestionStatusEnum] = None,
    current_user: User = Depends(require_role(UserRoleEnum.REVIEWER)),
    db: Session = Depends(get_db)
):
    """List ingestion queue items. Requires REVIEWER role or higher."""
    query = db.query(IngestionQueue)

    if status:
        query = query.filter(IngestionQueue.status == status)

    total = query.count()
    items = query.order_by(IngestionQueue.created_at.desc()).offset(skip).limit(limit).all()

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": items
    }


@router.get("/{queue_id}", response_model=IngestionQueueResponse)
def get_queue_item(
    queue_id: str,
    current_user: User = Depends(require_role(UserRoleEnum.REVIEWER)),
    db: Session = Depends(get_db)
):
    """Get queue item by ID. Requires REVIEWER role or higher."""
    item = db.query(IngestionQueue).filter(IngestionQueue.id == queue_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Queue item not found")
    return item


@router.put("/{queue_id}", response_model=IngestionQueueResponse)
def update_queue_item(
    queue_id: str,
    update: IngestionQueueUpdate,
    current_user: User = Depends(require_role(UserRoleEnum.REVIEWER)),
    db: Session = Depends(get_db)
):
    """Update queue item (approve/reject). Requires REVIEWER role or higher."""
    item = db.query(IngestionQueue).filter(IngestionQueue.id == queue_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Queue item not found")

    for field, value in update.model_dump(exclude_unset=True).items():
        setattr(item, field, value)

    db.commit()
    db.refresh(item)
    return item


@router.delete("/{queue_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_queue_item(
    queue_id: str,
    current_user: User = Depends(require_role(UserRoleEnum.EDITOR)),
    db: Session = Depends(get_db)
):
    """Delete queue item. Requires EDITOR role or higher."""
    item = db.query(IngestionQueue).filter(IngestionQueue.id == queue_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Queue item not found")

    db.delete(item)
    db.commit()


@router.post("/rss", response_model=RSSFeedIngestResponse, status_code=status.HTTP_201_CREATED)
def ingest_rss_feed(
    request: RSSFeedIngestRequest,
    current_user: User = Depends(require_role(UserRoleEnum.EDITOR)),
    db: Session = Depends(get_db)
):
    """Ingest RSS feed. Requires EDITOR role or higher."""
    try:
        queue_items = RSSIngester.ingest_feed(
            db=db,
            feed_url=request.feed_url,
            source_type=request.source_type,
            max_entries=request.max_entries
        )

        return {
            "feed_url": request.feed_url,
            "entries_added": len(queue_items),
            "entries": queue_items
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to ingest RSS feed: {str(e)}"
        )


@router.post("/youtube", response_model=YouTubeIngestResponse, status_code=status.HTTP_201_CREATED)
def ingest_youtube_video(
    request: YouTubeIngestRequest,
    current_user: User = Depends(require_role(UserRoleEnum.EDITOR)),
    db: Session = Depends(get_db)
):
    """Ingest YouTube video. Requires EDITOR role or higher."""
    try:
        queue_item = YouTubeIngester.ingest_video(
            db=db,
            video_url=request.video_url,
            title=request.title,
            author=request.author,
            published_date=request.published_date,
            languages=request.languages
        )

        if not queue_item:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to fetch video transcript"
            )

        video_id = YouTubeIngester.extract_video_id(request.video_url)

        return {
            "video_id": video_id,
            "queue_item": queue_item
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to ingest YouTube video: {str(e)}"
        )


@router.post("/pdf", response_model=PDFIngestResponse, status_code=status.HTTP_201_CREATED)
def ingest_pdf(
    request: PDFIngestRequest,
    current_user: User = Depends(require_role(UserRoleEnum.EDITOR)),
    db: Session = Depends(get_db)
):
    """Ingest PDF document. Requires EDITOR role or higher."""
    try:
        queue_item = PDFProcessor.ingest_pdf(
            db=db,
            pdf_url=request.pdf_url,
            title=request.title,
            author=request.author,
            published_date=request.published_date,
            source_type=request.source_type,
            save_locally=request.save_locally
        )

        return {
            "pdf_url": request.pdf_url,
            "local_file_path": queue_item.extracted_data.get('local_file_path') if queue_item.extracted_data else None,
            "queue_item": queue_item
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to ingest PDF: {str(e)}"
        )


@router.post("/tasks/trigger-all-feeds")
def trigger_all_feeds(
    current_user: User = Depends(require_role(UserRoleEnum.EDITOR))
) -> Dict:
    """
    Manually trigger ingestion of all configured RSS feeds. Requires EDITOR role or higher.

    Returns task ID for tracking.
    """
    try:
        task = ingest_all_feeds.delay()
        return {
            "task_id": task.id,
            "status": "queued",
            "message": "Feed ingestion task has been queued"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to queue ingestion task: {str(e)}"
        )


@router.post("/tasks/trigger-rss-feed")
def trigger_rss_feed(
    request: RSSFeedIngestRequest,
    current_user: User = Depends(require_role(UserRoleEnum.EDITOR))
) -> Dict:
    """
    Manually trigger ingestion of a specific RSS feed via Celery task. Requires EDITOR role or higher.

    Returns task ID for tracking.
    """
    try:
        task = ingest_rss_task.delay(
            feed_url=request.feed_url,
            source_type=request.source_type.value,
            max_entries=request.max_entries
        )
        return {
            "task_id": task.id,
            "feed_url": request.feed_url,
            "status": "queued",
            "message": "RSS feed ingestion task has been queued"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to queue RSS feed task: {str(e)}"
        )


@router.get("/tasks/{task_id}")
def get_task_status(task_id: str) -> Dict:
    """
    Get status of a Celery task.

    Returns task state and result if available.
    """
    try:
        task_result = AsyncResult(task_id)

        response = {
            "task_id": task_id,
            "status": task_result.state,
        }

        if task_result.ready():
            if task_result.successful():
                response["result"] = task_result.result
            else:
                response["error"] = str(task_result.info)

        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task not found: {str(e)}"
        )
