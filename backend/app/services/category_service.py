"""Category service for business logic."""
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models import Category
from app.schemas.category import CategoryCreate, CategoryUpdate


class CategoryService:
    """Service for category operations."""

    @staticmethod
    def create(db: Session, category: CategoryCreate) -> Category:
        """Create a new category."""
        db_category = Category(**category.model_dump())
        db.add(db_category)
        db.commit()
        db.refresh(db_category)
        return db_category

    @staticmethod
    def get_by_id(db: Session, category_id: str) -> Optional[Category]:
        """Get category by ID."""
        return db.query(Category).filter(Category.id == category_id).first()

    @staticmethod
    def get_by_name(db: Session, name: str) -> Optional[Category]:
        """Get category by name."""
        return db.query(Category).filter(Category.name == name).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[Category]:
        """Get all categories with pagination."""
        return db.query(Category).offset(skip).limit(limit).all()

    @staticmethod
    def get_count(db: Session) -> int:
        """Get total count of categories."""
        return db.query(Category).count()

    @staticmethod
    def update(db: Session, category_id: str, category_update: CategoryUpdate) -> Optional[Category]:
        """Update a category."""
        db_category = db.query(Category).filter(Category.id == category_id).first()
        if not db_category:
            return None

        update_data = category_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_category, key, value)

        db.commit()
        db.refresh(db_category)
        return db_category

    @staticmethod
    def delete(db: Session, category_id: str) -> bool:
        """Delete a category."""
        db_category = db.query(Category).filter(Category.id == category_id).first()
        if not db_category:
            return False

        db.delete(db_category)
        db.commit()
        return True
