from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.models.customer_tag import CustomerTag
from app.schemas.tag import TagCreate


class TagService:
    def __init__(self, db: Session):
        self.db = db

    def create_tag(self, tag: TagCreate) -> CustomerTag:
        """
        Create a new tag for a customer.
        """
        db_tag = CustomerTag(
            customer_id=tag.customer_id,
            label=tag.label,
            color=tag.color,
            priority=tag.priority,
            created_by=tag.created_by,
        )
        self.db.add(db_tag)
        self.db.commit()
        self.db.refresh(db_tag)
        return db_tag

    def get_tag(self, tag_id: UUID) -> Optional[CustomerTag]:
        """
        Get a tag by ID.
        """
        return self.db.query(CustomerTag).filter(CustomerTag.id == tag_id).first()

    def get_tags_by_customer(self, customer_id: UUID) -> List[CustomerTag]:
        """
        Get all tags for a specific customer.
        """
        return self.db.query(CustomerTag).filter(CustomerTag.customer_id == customer_id).all()

    def delete_tag(self, tag_id: UUID) -> bool:
        """
        Delete a tag.
        """
        db_tag = self.get_tag(tag_id)
        if not db_tag:
            return False
            
        self.db.delete(db_tag)
        self.db.commit()
        return True
