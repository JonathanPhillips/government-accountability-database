"""PDF document processing service."""
import os
import requests
from typing import Optional, Dict
from datetime import datetime
from PyPDF2 import PdfReader
from io import BytesIO
from sqlalchemy.orm import Session

from app.models import IngestionQueue
from app.models.base import SourceTypeEnum


class PDFProcessor:
    """Service for processing PDF documents."""

    @staticmethod
    def download_pdf(url: str) -> bytes:
        """Download PDF from URL."""
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            # Verify it's a PDF
            content_type = response.headers.get('content-type', '')
            if 'pdf' not in content_type.lower():
                # Try to detect by content
                if not response.content.startswith(b'%PDF'):
                    raise ValueError("URL does not point to a PDF file")

            return response.content
        except Exception as e:
            raise Exception(f"Failed to download PDF: {str(e)}")

    @staticmethod
    def extract_text_from_pdf(pdf_data: bytes) -> str:
        """Extract text content from PDF."""
        try:
            pdf_file = BytesIO(pdf_data)
            reader = PdfReader(pdf_file)

            text_content = []
            for page_num, page in enumerate(reader.pages, 1):
                try:
                    text = page.extract_text()
                    if text.strip():
                        text_content.append(f"--- Page {page_num} ---\n{text}")
                except Exception as e:
                    print(f"Error extracting text from page {page_num}: {str(e)}")
                    continue

            return '\n\n'.join(text_content)
        except Exception as e:
            raise Exception(f"Failed to extract text from PDF: {str(e)}")

    @staticmethod
    def extract_metadata(pdf_data: bytes) -> Dict:
        """Extract metadata from PDF."""
        try:
            pdf_file = BytesIO(pdf_data)
            reader = PdfReader(pdf_file)

            metadata = {}
            if reader.metadata:
                metadata = {
                    'title': reader.metadata.get('/Title', ''),
                    'author': reader.metadata.get('/Author', ''),
                    'subject': reader.metadata.get('/Subject', ''),
                    'creator': reader.metadata.get('/Creator', ''),
                    'producer': reader.metadata.get('/Producer', ''),
                    'creation_date': reader.metadata.get('/CreationDate', ''),
                    'modification_date': reader.metadata.get('/ModDate', '')
                }

            metadata['page_count'] = len(reader.pages)
            return metadata
        except Exception as e:
            print(f"Error extracting PDF metadata: {str(e)}")
            return {}

    @staticmethod
    def save_pdf_locally(
        pdf_data: bytes,
        filename: str,
        storage_dir: str = '/app/data/pdfs'
    ) -> str:
        """Save PDF to local storage."""
        try:
            # Create directory if it doesn't exist
            os.makedirs(storage_dir, exist_ok=True)

            # Generate safe filename
            safe_filename = "".join(
                c for c in filename if c.isalnum() or c in (' ', '.', '_', '-')
            ).rstrip()

            if not safe_filename.endswith('.pdf'):
                safe_filename += '.pdf'

            file_path = os.path.join(storage_dir, safe_filename)

            # Save file
            with open(file_path, 'wb') as f:
                f.write(pdf_data)

            return file_path
        except Exception as e:
            raise Exception(f"Failed to save PDF: {str(e)}")

    @staticmethod
    def add_to_queue(
        db: Session,
        source_url: str,
        title: str,
        content: str,
        author: Optional[str] = None,
        published_date: Optional[datetime] = None,
        local_file_path: Optional[str] = None,
        metadata: Optional[Dict] = None,
        source_type: SourceTypeEnum = SourceTypeEnum.COURT_FILING
    ) -> IngestionQueue:
        """Add PDF document to ingestion queue."""
        queue_item = IngestionQueue(
            source_url=source_url,
            source_type=source_type,
            raw_content=content,
            extracted_data={
                'title': title,
                'author': author,
                'published_date': published_date.isoformat() if published_date else None,
                'local_file_path': local_file_path,
                'file_type': 'pdf',
                **(metadata or {})
            }
        )

        db.add(queue_item)
        db.commit()
        db.refresh(queue_item)

        return queue_item

    @staticmethod
    def ingest_pdf(
        db: Session,
        pdf_url: str,
        title: str,
        author: Optional[str] = None,
        published_date: Optional[datetime] = None,
        source_type: SourceTypeEnum = SourceTypeEnum.COURT_FILING,
        save_locally: bool = True
    ) -> IngestionQueue:
        """Ingest PDF document and add to queue."""
        # Download PDF
        pdf_data = PDFProcessor.download_pdf(pdf_url)

        # Extract text
        text_content = PDFProcessor.extract_text_from_pdf(pdf_data)

        # Extract metadata
        pdf_metadata = PDFProcessor.extract_metadata(pdf_data)

        # Use metadata if title/author not provided
        if not title and pdf_metadata.get('title'):
            title = pdf_metadata['title']
        if not author and pdf_metadata.get('author'):
            author = pdf_metadata['author']

        # Save locally if requested
        local_path = None
        if save_locally:
            filename = title if title else f"document_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            try:
                local_path = PDFProcessor.save_pdf_locally(pdf_data, filename)
            except Exception as e:
                print(f"Warning: Could not save PDF locally: {str(e)}")

        # Add to queue
        return PDFProcessor.add_to_queue(
            db=db,
            source_url=pdf_url,
            title=title,
            content=text_content,
            author=author,
            published_date=published_date,
            local_file_path=local_path,
            metadata=pdf_metadata,
            source_type=source_type
        )
