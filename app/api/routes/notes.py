from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.db.database import get_db
from app.schemas.note import NoteCreatePayload, NoteResponse
from app.services.note_service import NoteService

customer_router = APIRouter()


@customer_router.post(
    "/{customer_id}/notes",
    response_model=NoteResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_customer_note(
    customer_id: UUID,
    note: NoteCreatePayload,
    db: Session = Depends(get_db),
):
    """Create a note for a specific customer."""
    service = NoteService(db)
    return service.create_customer_note(customer_id, note)


@customer_router.get(
    "/{customer_id}/notes",
    response_model=List[NoteResponse],
)
def get_customer_notes(
    customer_id: UUID,
    db: Session = Depends(get_db),
):
    """Retrieve all notes for a customer."""
    service = NoteService(db)
    return service.get_notes_by_customer(customer_id)


@customer_router.delete(
    "/{customer_id}/notes/{note_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_customer_note(
    customer_id: UUID,
    note_id: UUID,
    db: Session = Depends(get_db),
):
    """Delete a specific note for a customer."""
    service = NoteService(db)
    success = service.delete_customer_note(customer_id, note_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return None
