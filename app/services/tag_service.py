from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.models.customer_tag import CustomerTag
from app.schemas.tag import TagCreate


class TagService:
    def __init__(self, db: Session):
        self.db = db

    def create_tag(self, tag: TagCreate, trace_id: str) -> CustomerTag:
        """Create a single tag for a customer."""
        return self.create_tags(
            tag.customer_id,
            [tag.label],
            tag.color,
            tag.priority,
            tag.created_by,
            trace_id,
        )[0]

    def create_tags(
        self,
        customer_id: UUID,
        labels: List[str],
        color: Optional[str] = None,
        priority: int = 0,
        created_by: Optional[UUID] = None,
        trace_id: str = "",
    ) -> List[CustomerTag]:
        """Create multiple tags in one call."""
        db_tags = [
            CustomerTag(
                customer_id=customer_id,
                label=lbl,
                color=color,
                priority=priority,
                created_by=created_by,
            )
            for lbl in labels
        ]
        self.db.add_all(db_tags)
        self.db.commit()
        for tag in db_tags:
            self.db.refresh(tag)

        from app.services.event_publisher import publish_event_sync

        for tag in db_tags:
            payload = {
                "customer_id": str(tag.customer_id),
                "tag_id": str(tag.id),
                "label": tag.label,
                "trace_id": trace_id,
            }
            publish_event_sync("v1.customer.tagged", payload, trace_id)

        return db_tags

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
