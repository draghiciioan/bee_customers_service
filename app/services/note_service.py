from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from uuid import UUID
import logging

from app.models.customer_note import CustomerNote
from app.schemas.note import NoteCreate, NoteCreatePayload
from app.services.log_service import send_log


class NoteService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.logger = logging.getLogger(__name__)

    async def create_note(self, note: NoteCreate, trace_id: str) -> CustomerNote:
        """
        Create a new note for a customer.
        """
        db_note = CustomerNote(
            customer_id=note.customer_id,
            content=note.content,
            created_by=note.created_by,
        )
        self.db.add(db_note)
        await self.db.commit()
        await self.db.refresh(db_note)

        self.logger.info(
            "Note created",
            extra={
                "customer_id": str(db_note.customer_id),
                "note_id": str(db_note.id),
                "trace_id": trace_id,
            },
        )
        await send_log(
            "v1.customer.note_added",
            {"customer_id": str(db_note.customer_id), "note_id": str(db_note.id)},
            trace_id,
        )

        from app.services.event_publisher import publish_event

        payload = {
            "customer_id": str(db_note.customer_id),
            "note_id": str(db_note.id),
            "trace_id": trace_id,
        }
        await publish_event("v1.customer.note_added", payload, trace_id)

        return db_note

    async def create_customer_note(
        self, customer_id: UUID, payload: NoteCreatePayload, trace_id: str
    ) -> CustomerNote:
        """Create a note when the customer_id is provided separately."""
        data = NoteCreate(
            customer_id=customer_id,
            content=payload.content,
            created_by=payload.created_by,
        )
        return await self.create_note(data, trace_id)

    async def get_note(self, note_id: UUID) -> Optional[CustomerNote]:
        """
        Get a note by ID.
        """
        result = await self.db.execute(
            select(CustomerNote).where(CustomerNote.id == note_id)
        )
        return result.scalars().first()

    async def get_notes_by_customer(self, customer_id: UUID) -> List[CustomerNote]:
        """
        Get all notes for a specific customer.
        """
        result = await self.db.execute(
            select(CustomerNote).where(CustomerNote.customer_id == customer_id)
        )
        return result.scalars().all()

    async def delete_note(self, note_id: UUID) -> bool:
        """
        Delete a note.
        """
        db_note = await self.get_note(note_id)
        if not db_note:
            return False

        await self.db.delete(db_note)
        await self.db.commit()
        return True

    async def delete_customer_note(self, customer_id: UUID, note_id: UUID) -> bool:
        """Delete a note belonging to a specific customer."""
        result = await self.db.execute(
            select(CustomerNote).where(
                CustomerNote.id == note_id,
                CustomerNote.customer_id == customer_id,
            )
        )
        db_note = result.scalars().first()
        if not db_note:
            return False
        await self.db.delete(db_note)
        await self.db.commit()
        return True
