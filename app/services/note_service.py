from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.models.customer_note import CustomerNote
from app.schemas.note import NoteCreate, NoteCreatePayload


class NoteService:
    def __init__(self, db: Session):
        self.db = db

    def create_note(self, note: NoteCreate) -> CustomerNote:
        """
        Create a new note for a customer.
        """
        db_note = CustomerNote(
            customer_id=note.customer_id,
            content=note.content,
            created_by=note.created_by
        )
        self.db.add(db_note)
        self.db.commit()
        self.db.refresh(db_note)
        return db_note

    def create_customer_note(
        self, customer_id: UUID, payload: NoteCreatePayload
    ) -> CustomerNote:
        """Create a note when the customer_id is provided separately."""
        data = NoteCreate(
            customer_id=customer_id,
            content=payload.content,
            created_by=payload.created_by,
        )
        return self.create_note(data)

    def get_note(self, note_id: UUID) -> Optional[CustomerNote]:
        """
        Get a note by ID.
        """
        return self.db.query(CustomerNote).filter(CustomerNote.id == note_id).first()

    def get_notes_by_customer(self, customer_id: UUID) -> List[CustomerNote]:
        """
        Get all notes for a specific customer.
        """
        return self.db.query(CustomerNote).filter(CustomerNote.customer_id == customer_id).all()

    def delete_note(self, note_id: UUID) -> bool:
        """
        Delete a note.
        """
        db_note = self.get_note(note_id)
        if not db_note:
            return False
            
        self.db.delete(db_note)
        self.db.commit()
        return True

    def delete_customer_note(self, customer_id: UUID, note_id: UUID) -> bool:
        """Delete a note belonging to a specific customer."""
        db_note = (
            self.db.query(CustomerNote)
            .filter(
                CustomerNote.id == note_id,
                CustomerNote.customer_id == customer_id,
            )
            .first()
        )
        if not db_note:
            return False
        self.db.delete(db_note)
        self.db.commit()
        return True
