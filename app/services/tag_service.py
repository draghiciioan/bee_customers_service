from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from uuid import UUID
import logging

from app.models.customer_tag import CustomerTag
from app.schemas.tag import TagCreate
from app.services.log_service import send_log


class TagService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.logger = logging.getLogger(__name__)

    async def create_tag(self, tag: TagCreate, trace_id: str) -> CustomerTag:
        """Create a single tag for a customer."""
        result = await self.create_tags(
            tag.customer_id,
            [tag.label],
            tag.color,
            tag.priority,
            tag.created_by,
            trace_id,
        )
        return result[0]

    async def create_tags(
        self,
        customer_id: UUID,
        labels: List[str],
        color: Optional[str] = None,
        priority: int = 0,
        created_by: Optional[UUID] = None,
        trace_id: str = "",
    ) -> List[CustomerTag]:
        """Create multiple tags in one call.

        Raises ``ValueError`` if any requested label already exists for the
        customer or if duplicate labels are provided in the request.
        """

        # Check for duplicates in the payload
        unique_labels = list(dict.fromkeys(labels))
        if len(unique_labels) != len(labels):
            raise ValueError("Duplicate labels provided")

        # Check for existing tags with the same labels
        stmt = (
            select(CustomerTag.label)
            .where(
                CustomerTag.customer_id == customer_id,
                CustomerTag.label.in_(unique_labels),
            )
        )
        result = await self.db.execute(stmt)
        existing_labels = {row.label for row in result.all()}
        if existing_labels:
            joined = ", ".join(sorted(existing_labels))
            raise ValueError(f"Tag(s) already exist: {joined}")

        db_tags = [
            CustomerTag(
                customer_id=customer_id,
                label=lbl,
                color=color,
                priority=priority,
                created_by=created_by,
            )
            for lbl in unique_labels
        ]
        self.db.add_all(db_tags)
        await self.db.commit()
        for tag in db_tags:
            await self.db.refresh(tag)

        for tag in db_tags:
            self.logger.info(
                "Customer tagged",
                extra={
                    "customer_id": str(tag.customer_id),
                    "tag_id": str(tag.id),
                    "trace_id": trace_id,
                },
            )
            from app.services.log_service import send_log

            await send_log(
                "v1.customer.tagged",
                {
                    "customer_id": str(tag.customer_id),
                    "tag_id": str(tag.id),
                    "label": tag.label,
                },
                trace_id,
            )

        from app.services.event_publisher import publish_event

        for tag in db_tags:
            payload = {
                "customer_id": str(tag.customer_id),
                "tag_id": str(tag.id),
                "label": tag.label,
                "trace_id": trace_id,
            }
            await publish_event("v1.customer.tagged", payload, trace_id)

        return db_tags

    async def get_tag(self, tag_id: UUID) -> Optional[CustomerTag]:
        """
        Get a tag by ID.
        """
        result = await self.db.execute(
            select(CustomerTag).where(CustomerTag.id == tag_id)
        )
        return result.scalars().first()

    async def get_tags_by_customer(self, customer_id: UUID) -> List[CustomerTag]:
        """
        Get all tags for a specific customer.
        """
        result = await self.db.execute(
            select(CustomerTag).where(CustomerTag.customer_id == customer_id)
        )
        return result.scalars().all()

    async def delete_tag(self, tag_id: UUID) -> bool:
        """
        Delete a tag.
        """
        db_tag = await self.get_tag(tag_id)
        if not db_tag:
            return False

        await self.db.delete(db_tag)
        await self.db.commit()
        return True

    async def delete_customer_tag(self, customer_id: UUID, tag_id: UUID) -> bool:
        """Delete a tag belonging to a specific customer."""
        result = await self.db.execute(
            select(CustomerTag).where(
                CustomerTag.id == tag_id,
                CustomerTag.customer_id == customer_id,
            )
        )
        db_tag = result.scalars().first()
        if not db_tag:
            return False
        await self.db.delete(db_tag)
        await self.db.commit()
        return True
