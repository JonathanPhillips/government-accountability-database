"""Ingestion schemas."""
from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict
from datetime import datetime

from app.models.base import SourceTypeEnum, IngestionStatusEnum


# Base schemas
class IngestionQueueBase(BaseModel):
    source_url: str
    source_type: SourceTypeEnum
    raw_content: Optional[str] = None
    extracted_data: Optional[Dict] = None


class IngestionQueueCreate(IngestionQueueBase):
    pass


class IngestionQueueUpdate(BaseModel):
    status: Optional[IngestionStatusEnum] = None
    raw_content: Optional[str] = None
    extracted_data: Optional[Dict] = None


class IngestionQueueResponse(IngestionQueueBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    status: IngestionStatusEnum
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    created_incident_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime


# RSS Feed Ingestion
class RSSFeedIngestRequest(BaseModel):
    feed_url: str
    source_type: SourceTypeEnum = SourceTypeEnum.NEWS_PRIMARY
    max_entries: Optional[int] = 10


class RSSFeedIngestResponse(BaseModel):
    feed_url: str
    entries_added: int
    entries: list[IngestionQueueResponse]


# YouTube Ingestion
class YouTubeIngestRequest(BaseModel):
    video_url: str
    title: str
    author: Optional[str] = None
    published_date: Optional[datetime] = None
    languages: list[str] = ['en']


class YouTubeIngestResponse(BaseModel):
    video_id: str
    queue_item: IngestionQueueResponse


# PDF Ingestion
class PDFIngestRequest(BaseModel):
    pdf_url: str
    title: str
    author: Optional[str] = None
    published_date: Optional[datetime] = None
    source_type: SourceTypeEnum = SourceTypeEnum.COURT_FILING
    save_locally: bool = True


class PDFIngestResponse(BaseModel):
    pdf_url: str
    local_file_path: Optional[str]
    queue_item: IngestionQueueResponse
