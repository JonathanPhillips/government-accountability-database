"""Category model."""
from sqlalchemy import Column, String, Text
from app.database import Base
from .base import generate_uuid, TimestampMixin


class Category(Base, TimestampMixin):
    """Primary categorization for incidents."""

    __tablename__ = "categories"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String(200), nullable=False, unique=True)
    description = Column(Text, nullable=False)

    def __repr__(self):
        return f"<Category(id='{self.id}', name='{self.name}')>"
